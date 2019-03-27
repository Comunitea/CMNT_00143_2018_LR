# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    date_start_payment = fields.Date(
        string='Date Start',
        default=fields.Date.context_today,
    )
    date_end_payment = fields.Date(
        string='Date End',
        index=True,
    )
    recurring_payment = fields.Boolean(
        string='Generate recurring payments automatically',
    )
    recurring_payment_next_date = fields.Date(
        default=fields.Date.context_today,
        copy=False,
        string='Date of Next Payment',
    )
    payment_qty = fields.Float(string='Payment quantity')

    date_start_voucher = fields.Date(
        string='Date Start',
        default=fields.Date.context_today,
    )
    date_end_voucher = fields.Date(
        string='Date End Contract',
        index=True,
    )
    recurring_voucher = fields.Boolean(
        string='Generate recurring vouchers automatically',
    )
    recurring_voucher_end_date = fields.Date(
        default=fields.Date.context_today,
        copy=False,
        string='Date Last Voucher',
    )
    voucher_qty = fields.Float(string='Voucher quantity')
    total_voucher_qty = fields.Float(string='Total vouchers quantity')
    number_vouchers = fields.Integer(string='Number of vouchers')
    voucher_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal Voucher',)
    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate',
        string='Mandate',)
    res_partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Bank', )
    day_due = fields.Integer(string='Due day', default=25)
    #supplier_id = fields.Many2one(comodel_name='res.partner',
    #    string='Supplier', domain=[('supplier', '=', True),
    #                               ('company_type', '=', 'company')])
    #payment_mode_invoice_id = fields.Many2one(
    #    comodel_name='account.payment.mode',
    #    string='Payment mode for Invoices',
    #    domain=[('payment_type', '=', 'inbound')])
    account_id = fields.Many2one(comodel_name='account.account',
                                  string='Voucher Account')
    next_voucher_number = fields.Integer(string='Next Voucher Number',
                                         default=1)
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        domain=[]
    )

    def get_first_due_date(self):
        start_date = fields.Datetime.from_string(
            self.date_start_voucher)
        first_due = start_date
        if self.day_due:
            if start_date.day > self.day_due:
                first_due = first_due.replace(day=self.day_due)
                first_due = first_due + self.get_relative_delta(
                    self.recurring_voucher_rule_type,
                    self.recurring_voucher_interval)
            else:
                first_due = first_due.replace(day=self.day_due)
        return first_due

    @api.onchange('number_vouchers', 'recurring_voucher_rule_type',
                  'recurring_voucher_interval', 'day_due',
                  'date_start_voucher')
    def onchange_dates(self):
        first_due = self.get_first_due_date()

        self.recurring_voucher_end_date = \
            first_due + \
            self.get_relative_delta(self.recurring_voucher_rule_type,
                                    self.recurring_voucher_interval) * \
            (self.number_vouchers - 1)


    @api.onchange( 'total_voucher_qty', 'number_vouchers')
    def onchange_amount_total(self):
        if self.number_vouchers:
            self.voucher_qty = self.total_voucher_qty / \
                                   self.number_vouchers

    @api.onchange('voucher_qty', 'number_vouchers')
    def onchange_amount(self):
            self.total_voucher_qty = self.voucher_qty * \
                                     self.number_vouchers

    @api.multi
    def _prepare_invoice(self, journal=None):
        res = super(AccountAnalyticAccount, self)._prepare_invoice()
        res['partner_id'] = self.partner_id.id
        return res

    @api.model
    def create_recurring_payments(self):
        today = fields.Date.today()
        contracts = self.with_context(cron=True).search([
            ('recurring_payment', '=', True),
            ('recurring_payment_next_date', '<=', today),
            '|',
            ('date_end_payment', '=', False),
            ('date_end_payment', '>=', today),
        ])
        return contracts.recurring_create_payment()

    def recurring_create_payment(self):
        for contract in self:
            ref_date = contract.recurring_payment_next_date or \
                fields.Date.today()
            if (contract.date_start_payment > ref_date or
                    contract.date_end_payment and contract.date_end_payment <
                    ref_date):
                if self.env.context.get('cron'):
                    continue  # Don't fail on cron jobs
                raise ValidationError(
                    _("You must review start and end payment dates!\n%s") %
                    contract.name
                )
            old_date = fields.Date.from_string(ref_date)
            new_date = old_date + self.get_relative_delta(
                contract.recurring_payment_rule_type,
                contract.recurring_payment_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluation of domain access rules
                'force_company': contract.company_id.id,
            })
            self = self.with_context(ctx)
            # Re-read contract with correct company
            mandate = self.env['account.banking.mandate'].search(
                [('partner_id', '=', contract.partner_id.id),
                 ('state', '=', 'valid')], limit=1)
            if not mandate:
                self.message_post(_('can not find a customer mandate'))
                continue
            payment_order = self.env['account.payment.order'].search(
                [('payment_mode_id', '=', contract.payment_mode_id.id),
                 ('state', '=', 'draft')], limit=1)
            if not payment_order:
                payment_order = self.env['account.payment.order'].create(
                    {'payment_mode_id': contract.payment_mode_id.id,
                     'payment_type': 'inbound'})
            self.env['account.payment.line'].create({
                'order_id': payment_order.id,
                'currency_id': contract.currency_id.id,
                'partner_id': contract.partner_id.id,
                'mandate_id': mandate.id,
                'partner_bank_id': mandate.partner_bank_id.id,
                'amount_currency': contract.payment_qty,
                'communication': contract.name
            })
            contract.write({
                'recurring_payment_next_date': fields.Date.to_string(new_date)
            })

    @api.model
    def recurring_create_vouchers(self):
        today = fields.Date.today()
        contracts = self.with_context(cron=True).search([
            ('recurring_voucher', '=', True),
            ('recurring_payment_next_date', '<=', today),
            '|',
            ('date_start_voucher', '=', False),
            ('date_end_voucher', '>=', today),
        ])
        return contracts.recurring_create_voucher()

    def recurring_create_voucher(self):
        for contract in self:

            first_due = self.get_first_due_date()

            ctx = self.env.context.copy()
            ctx.update({
                'old_date': first_due,
                # Force company for correct evaluation of domain access rules
                'force_company': contract.company_id.id,
            })
            self = self.with_context(ctx)
            # Re-read contract with correct company
            if contract.contract_type == 'sale':
                mandate = self.env['account.banking.mandate'].search(
                    [('partner_id', '=', contract.partner_id.id),
                     ('state', '=', 'valid')], limit=1)
                if not mandate:
                    self.message_post(_('can not find a customer mandate'))
                    continue
            else:
                res_partner_bank_id = self.env[
                    'res.partner.bank'].search(
                    [('partner_id', '=', contract.partner_id.id)], limit=1) \
                                      or False
            iter_num = 1
            date = first_due
            total_amount =0
            while iter_num <= contract.number_vouchers:
                voucher_number = contract.next_voucher_number +iter_num -1
                name = "%s.%d" % (contract.name, voucher_number)
                if contract.contract_type == 'sale':
                    account_voucher = self.env['account.voucher'].create(
                        {'partner_id': contract.partner_id.id,
                         'pay_now': 'pay_later',
                         'company_id': contract.company_id.id,
                         'account_id':
                             contract.partner_id.property_account_receivable_id
                                 .id,
                         'journal_id': contract.voucher_journal_id.id,
                         'account_date': fields.Date.to_string(date),
                         'date_due': fields.Date.to_string(date),
                         'mandate_id': contract.mandate_id.id,
                         'payment_mode_id': contract.payment_mode_id.id,
                         'contract_id': contract.id,
                         'voucher_type': 'sale',
                         'number': name
                         })
                else:
                    account_voucher = self.env['account.voucher'].create(
                        {'partner_id': contract.partner_id.id,
                         'pay_now': 'pay_later',
                         'company_id': contract.company_id.id,
                         'account_id':
                             contract.partner_id.property_account_payable_id
                                 .id,
                         'journal_id': contract.voucher_journal_id.id,
                         'account_date': fields.Date.to_string(date),
                         'date_due': fields.Date.to_string(date),
                         'res_partner_bank_id': res_partner_bank_id and
                                                res_partner_bank_id.id,
                         'payment_mode_id': contract.payment_mode_id.id,
                         'contract_id': contract.id,
                         'voucher_type': 'purchase',
                         'number': name
                         })

                if iter_num == contract.number_vouchers:
                    amount = contract.total_voucher_qty - total_amount
                else:
                    amount = contract.voucher_qty
                self.env['account.voucher.line'].create({
                    'voucher_id': account_voucher.id,
                    'name': name,
                    'account_id': contract.account_id.id,
                    'account_analytic_id': contract.id,
                    'company_id': contract.company_id.id,
                    'quantity': 1,
                    'price_unit': amount
                })
                iter_num += 1
                total_amount += amount
                date = date + self.get_relative_delta(
                    contract.recurring_voucher_rule_type,
                    contract.recurring_voucher_interval)
                account_voucher.proforma_voucher()
                account_voucher.write({
                    'number': name
                })
