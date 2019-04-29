
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class VirtualFair(models.Model):

    _name = 'virtual.fair'

    name = fields.Char('Name')
    id_name = fields.Char('ID Name')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    customer_ids = fields.One2many(comodel_name='fair.customer.line',
                                   inverse_name='fair_id', string='Customers')
    supplier_ids = fields.One2many(comodel_name='fair.supplier.line',
                                   inverse_name='fair_id', string='Suppliers')

    def invoice_suppliers(self):
        invoices = self.env['account.invoice']
        for supplier in self.supplier_ids.mapped('supplier_id'):
            for rule_type in ('DESCUENTO_PCT', 'DESCUENTO_EUR'):
                rule = self.env['fair.supplier.line'].search([
                    ('fair_id', '=', self.id),
                    ('supplier_id', '=', supplier.id),
                    ('condition_type', '=', rule_type)
                ])
                if not rule:
                    rule = self.env['fair.supplier.line'].search([
                        ('fair_id', '=', self.id),
                        ('supplier_id', '=', False),
                        ('condition_type', '=', rule_type)
                    ])
                if rule:
                    if rule_type == 'DESCUENTO_EUR':
                        quantity = rule.value
                        quantity = float(quantity.replace(',', '.'))
                    else:
                        supplier_invoices = self.env['account.invoice'].search(
                            [('fair_id', '=', self.id),
                             ('type', '=', 'in_invoice'),
                             ('partner_id', '=', supplier.id)])
                        quantity = sum(supplier_invoices.mapped('amount_untaxed'))
                        perc = rule.value
                        perc = float(perc.replace(',', '.'))
                        quantity = quantity * (perc / 100)
                    if quantity <= 0:
                        continue
                    vals = {
                        'partner_id': supplier.id,
                        'type': 'out_invoice',
                        'fair_id': self.id,
                    }

                    vals = self.env['account.invoice'].play_onchanges(
                        vals, ['partner_id'])
                    invoice = self.env['account.invoice'].create(vals)

                    line_vals = {
                        'invoice_id': invoice.id,
                        'name': rule_type,
                        'quantity': 1,
                        'price_unit': quantity,
                        'product_id': self.env.ref('virtual_fair.fair_incomes').id,
                    }
                    line_vals = self.env['account.invoice.line'].play_onchanges(
                        line_vals, ['product_id'])
                    self.env['account.invoice.line'].create(line_vals)
                    invoice.compute_taxes()
                    invoices += invoice
        if invoices:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['domain'] = [('id', 'in', invoices._ids)]
            return action



class CustomerLines(models.Model):
    _name = 'fair.customer.line'
    _rec_name = 'ref_int'

    fair_id = fields.Many2one('virtual.fair', string='Fair')
    facturation = fields.Char('Facturation')
    ref_int = fields.Char('Ref Int')
    customer_type = fields.Char('Customer Type')
    condition_type = fields.Char('Condition Type')
    value = fields.Char('Value')
    customer_id = fields.Many2one('res.partner', 'Customer')
    term_id = fields.Many2one('account.payment.term', 'Payment Terms')


class SupplierLines(models.Model):
    _name = 'fair.supplier.line'
    _rec_name = 'ref_int'

    fair_id = fields.Many2one('virtual.fair', 'Fair')
    ref_int = fields.Char('Ref Int')
    condition_ids = fields.One2many('condition.line', 'line_id',
                                    'Conditions')
    facturation = fields.Char('Facturation')
    condition_type = fields.Char('Condition Type')
    value = fields.Char('Value')
    supplier_id = fields.Many2one('res.partner', 'Supplier')


class ConditionLine(models.Model):
    _name = 'condition.line'

    line_id = fields.Many2one('fair.supplier.line', 'Fair')
    facturation = fields.Char('Facturation')
    condition_type = fields.Char('Condition Type')
    section_ids = fields.One2many('section.line', 'condition_id',
                                  'Sections')


class SectionLine(models.Model):
    _name = 'section.line'

    condition_id = fields.Many2one('condition.line', string='Fair')
    ean = fields.Char('Ean')
    linf = fields.Float('LInf')
    lsup = fields.Float('LSup')
    value = fields.Char('Value')
    term_id = fields.Many2one('account.payment.term', 'Payment Terms')
