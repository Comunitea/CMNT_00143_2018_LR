# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
