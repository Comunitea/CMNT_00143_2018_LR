# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    def _error_exist(self):
        for inv in self:
            if inv.log_line_ids:
                inv.error_exist = True

    fair_id = fields.Many2one('virtual.fair', 'Virtual Fair')
    digit_date = fields.Date('Digit Date')
    num_ass = fields.Char('Num Associated')
    associate_id = fields.Many2one('res.partner', 'Associate')
    num_conf = fields.Char('Conformation number')
    featured = fields.Boolean('Featured')
    featured_percent = fields.Float('Featured Percent')
    log_id = fields.Many2one('importation.log', string='Log')
    log_line_ids = fields.One2many('log.line', 'invoice_id', string='Log')
    error_exist = fields.Boolean('Base error', compute='_error_exist')
    customer_invoice_id = fields.Many2one('account.invoice',
                                          'Customer Invoice')
    supplier_invoices_count = fields.Integer('# Suipplier Invoices',
                                             compute='_count_supplier_invoice')
    from_import = fields.Boolean('From supplier import', readonly=True)
    from_supplier = fields.Boolean('From supplier invoice', readonly=True)
    clean_reference = fields.Char(compute='_compute_clean_reference',
                                  store=True)
    tag = fields.Char('Tag')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', compute='_compute_analytic_account_id')
    customer_analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Contract account')
    force_no_group = fields.Boolean('Force No Group', default=False)
    supplier_maturity_date = fields.Boolean('Supllier Maturity Date')

    @api.multi
    def recalculate_maturity_date(self):
        for inv in self:
            if inv.supplier_maturity_date and inv.supplier_invoices_count == 1:
                domain = [('customer_invoice_id', '=', self.id)]
                sup_invoice = self.search(domain)[0]
                if sup_invoice.move_id:
                    move_lines_sup = self.env["account.move.line"]. \
                        search([('move_id', '=', sup_invoice.move_id.id),
                                ('account_id.internal_type', 'in',
                                 ['payable', 'receivable']),
                                ('date_maturity', "!=", False)],
                               order="date_maturity asc")
                    move_lines = self.env["account.move.line"]. \
                        search([('move_id', '=', inv.move_id.id),
                                ('account_id.internal_type', 'in',
                                 ['payable', 'receivable']),
                                ('date_maturity', "!=", False)],
                               order="date_maturity asc")
                    move_count = 0
                    days = []
                    payment_term_obj = self.env['account.payment.term']
                    if inv.commercial_partner_id.payment_days:
                        days = payment_term_obj._decode_payment_days(
                            inv.commercial_partner_id.payment_days)
                    for move_line in move_lines:
                        new_maturity = fields.Date.from_string(
                            move_lines_sup[move_count].date_maturity)
                        new_maturity = fields.Datetime.to_string(
                            new_maturity - timedelta(days=15))

                        new_date = False
                        date = fields.Date.from_string(new_maturity)

                        for day in days:
                            if date.day <= day:
                                new_date = payment_term_obj.next_day(date, day)
                                break

                        if days:
                            if not new_date:
                                day = days[0]
                                date = payment_term_obj.next_day(date, day)
                            else:
                                date = new_date

                        if not inv.commercial_partner_id.pays_during_holidays:
                            date = payment_term_obj._after_holidays(
                                inv.commercial_partner_id, date, days)
                        move_count += 1
                        move_line.write({'date_maturity': date})
                    inv.date_due = date
        return True

    def _compute_analytic_account_id(self):
        for invoice in self:
            analytic_accounts = invoice.mapped(
                'invoice_line_ids.account_analytic_id')
            if len(analytic_accounts) == 1:
                invoice.analytic_account_id = analytic_accounts
            else:
                invoice.analytic_account_id = False

    @api.depends('reference')
    def _compute_clean_reference(self):
        for invoice in self:
            invoice.clean_reference = invoice.reference and \
                re.sub('[^A-Za-z0-9]+', '', invoice.reference) or ''

    @api.multi
    def _count_supplier_invoice(self):
        for inv in self:
            domain = [('customer_invoice_id', '=', inv.id)]
            count = self.search_count(domain)
            inv.supplier_invoices_count = count

    @api.model
    def _refund_cleanup_lines(self, lines):
        super_lines = lines
        if lines._name == 'account.invoice.line' and \
                self._context.get('featured_error', False):
            for line in lines:
                if line.product_id.id != \
                        self.env.ref('virtual_fair.featured_product').id:
                    super_lines -= line
        elif lines._name == 'account.invoice.tax' and \
                self._context.get('featured_error', False):
            # En este caso no se copian los impuestos para forzar a
            # recalcularlos.
            return False
        res = super()._refund_cleanup_lines(super_lines)
        if lines._name == 'account.invoice.line' and \
                self._context.get('featured_error', False):
            for line in res:
                line[2]['price_unit'] = self._context.get('new_featured_price')
        return res

    @api.multi
    def action_view_supplier_invoices(self):
        """
        Smart button: View the origin supplier invoices
        """
        self.ensure_one()
        domain = [('customer_invoice_id', '=', self.id)]
        invoices = self.search(domain)
        action = self.env.ref('account.action_invoice_tree2').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def set_fair_supplier_conditions(self):
        """
        Change conditions based on virtual fair. Only search for payment terms
        """
        for inv in self:
            amount = inv.amount_total
            date_ref = fields.Date.from_string(inv.date_invoice)
            date_ref = fields.Datetime.to_string(date_ref - timedelta(
                days=30))
            domain = [
                ('supplier_id', '=', inv.partner_id.id),
                ('fair_id.condition_type', 'not in', ['DESCUENTO_EUR',
                                                      'DESCUENTO_PCT']),
                ('fair_id.date_start', '<=', inv.date_invoice),
                ('fair_id.date_end', '>=', date_ref),
            ]
            line = self.env['fair.supplier.line'].search(domain, limit=1)

            #Para establcer feria, debe estar también l alinea de cliente o
            # para todos
            domain = [
                ('fair_id', '=', line.fair_id.id),
                '|', ('customer_id', '=', inv.associate_id.id),
                ('customer_id', '=', False)
            ]
            customer_line = self.env['fair.customer.line'].\
                search(domain, limit=1, order='customer_id DESC')

            if not line or not customer_line:
                continue

            term_id = False
            if line.condition_type not in ['DESCUENTO_EUR', 'DESCUENTO_PCT']:
                for cond in line.condition_ids:
                    if cond.condition_type in ('PLAZO', 'PLAZO_TODOS'):
                        for s in cond.section_ids:
                            if amount >= s.linf and amount <= s.lsup:
                                term_id = s.term_id.id
                                break

            vals = {'fair_id': line.fair_id.id}
            if term_id:
                vals.update({'payment_term_id': term_id})
            inv.write(vals)
        return

    @api.multi
    def set_customer_fair_conditions(self):
        """
        Change conditions based on virtual fair. Only search for payment terms
        """
        invoice_obj = self.env['account.invoice']
        for inv in self:
            term_id = False
            if not inv.fair_id:
                continue
            vals = {}
            amount = inv.amount_total


            domain = [
                ('customer_id', '=', inv.commercial_partner_id.id),
                ('fair_id', '=', inv.fair_id.id),
            ]
            line = self.env['fair.customer.line'].search(domain, limit=1)
            if line:
                if line.condition_type in ['PLAZO',]:
                    term_id = line.term_id.id
            else:
                # comprobamos condiciones explícitas de proveedor (Nuevas
                # condiciones de plazo) si no es cliente "congelado"
                domain = [('customer_invoice_id', '=', inv.id)]
                sup_invoice = invoice_obj.search(domain)[0]
                domain = [
                    ('supplier_id', '=',
                     sup_invoice.commercial_partner_id.id),
                    ('fair_id', '=', inv.fair_id.id),
                ]
                sup_line = self.env['fair.supplier.line']. \
                    search(domain, limit=1)
                if sup_line:
                    if sup_line.condition_type not in ['DESCUENTO_EUR',
                                                       'DESCUENTO_PCT']:
                        for cond in sup_line.condition_ids:
                            if cond.condition_type in ('PLAZO_SOCIO',
                                                       'PLAZO_TODOS'):
                                for s in cond.section_ids:
                                    if amount >= s.linf and amount <= s.lsup:
                                        term_id = s.term_id.id
                                        if cond.condition_type == \
                                                'PLAZO_TODOS':
                                            vals.update(
                                                {'supplier_maturity_date': True})
                                        break
                if not term_id:
                    domain = [
                        ('customer_id', '=', False),
                        ('fair_id', '=', inv.fair_id.id),
                    ]
                    line = self.env['fair.customer.line'].search(domain,
                                                                 limit=1)
                    if line:
                        term_id = line.term_id.id

            if term_id:
                vals.update({'payment_term_id': term_id})
                inv.write(vals)
        return

    @api.multi
    def set_featured_line(self):
        """
        Creates a line with the collaboration product.
        For each origin supplier invoice, compute the featured percent, and
        adds a new line with the sum of this featured amounts
        """
        for inv in self:
            domain = [('customer_invoice_id', '=', inv.id)]
            supplier_invoices = self.search(domain)
            if not supplier_invoices:
                continue
            featured_percent = supplier_invoices[0].featured_percent
            featured_amount = 0.0
            for sinv in supplier_invoices:
                per = sinv.featured_percent
                featured_amount += (sinv.amount_untaxed * (per / 100.0))

            if featured_amount:
                # Get account
                cat = self.env['product.category'].search([], limit=1)
                product = self.env.ref('virtual_fair.featured_product')
                account = product.property_account_income_id or \
                             cat.property_account_income_categ_id
                account_id = inv.fiscal_position_id.map_account(account).id
                taxes = inv.fiscal_position_id.map_tax(product.taxes_id)
                line_vals = {
                    'name': "%s%% Colaboración" % featured_percent,
                    'product_id': product.id,
                    'quantity': 1.0,
                    'price_unit': featured_amount,
                    'account_id': account_id,
                    'invoice_id': inv.id,
                    'invoice_line_tax_ids': [(6, 0, taxes.ids)]
                }
                self.env['account.invoice.line'].create(line_vals)

        return

    @api.multi
    def set_supplier_featured_percent(self):
        """
        Check amount total and set the featured percent when import the
        supplier invoices
        """
        for inv in self:
            total = inv.amount_total
            if not inv.company_id:
                continue
            for line in inv.company_id.featured_line_ids:
                linf = line.linf
                lsup = line.lsup
                if (not linf or linf <= total) and (not lsup or lsup > total):
                    inv.write({'featured_percent': line.percent})

    @api.multi
    def set_supplier_analytic_account(self):
        for invoice in self:
            analytic_account = self.env['account.analytic.account'].search(
                [('recurring_voucher', '=', True),
                 ('contract_type', '=', 'purchase'),
                 ('partner_id', '=', invoice.commercial_partner_id.id)],
                limit=1)
            customer_analytic_account = self.env[
                'account.analytic.account'].search(
                [('recurring_voucher', '=', True),
                 ('supplier_id', '=', invoice.commercial_partner_id.id),
                 ('partner_id', '=', invoice.associate_id.id),
                 ('date_start_contract', '<=', invoice.date_invoice),
                 ('date_end_voucher', '>=', invoice.date_invoice),
                 ('contract_type', '=', 'sale')], limit=1)
            vals = {}
            if analytic_account:
                vals.update(account_analytic_id= analytic_account.id)
            if customer_analytic_account:
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag
                                    in customer_analytic_account.tag_ids]
                vals.update(analytic_tag_ids=analytic_tag_ids)
                invoice.write({'customer_analytic_account_id':
                                   customer_analytic_account.id })
            if vals:
                invoice.invoice_line_ids.write(vals)

    def check_duplicate_history(self):
        equal_args = [
            ('supplier_id', '=', self.partner_id.id),
            ('associate_id', '=', self.associate_id.id),
            ('fchaFra', '=', self.date_invoice),
            ('etiqueta', '!=', self.tag)]
        if not self._context.get('check_different_name'):
            equal_args.append(('clean_reference', '=', self.clean_reference))
        return self.env['account.invoice.history'].search(equal_args)

    def check_duplicate_supplier(self):
        self.ensure_one()
        if not self.reference:
            return False
        equal_args = [
             ('partner_id', '=', self.partner_id.id),
             ('associate_id', '=', self.associate_id.id),
             ('date_invoice', '=', self.date_invoice),
             ('id', '!=', self.id),
             ('tag', '!=', self.tag)]
        if not self._context.get('check_different_name'):
            equal_args.append(('clean_reference', '=', self.clean_reference))
        return self.env['account.invoice'].search(equal_args)

    def check_duplicate_all(self):
        duplicate = self.check_duplicate_supplier()
        duplicate_2 = self.check_duplicate_history()
        return duplicate or duplicate_2 or False

    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        from_supplier_invoices = self.filtered(lambda inv: inv.from_supplier)
        if from_supplier_invoices:
            invs = {}
            for inv in from_supplier_invoices:
                invs.setdefault(inv.date_invoice, self.env['account.invoice'])
                invs[inv.date_invoice] += inv
            for date, invoices in invs.items():
                domain = [('customer_invoice_id', 'in', invoices.ids),
                        ('type', 'in', ('in_invoice', 'in_refund')),
                        ('state', '=', 'draft')]
                supplier_invoices = self.search(domain)
                supplier_invoices.write({'date': date})
                supplier_invoices.action_invoice_open()
        self.recalculate_maturity_date()
        return res
