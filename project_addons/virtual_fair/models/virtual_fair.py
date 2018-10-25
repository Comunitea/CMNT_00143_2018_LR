
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


class CustomerLines(models.Model):
    _name = 'fair.customer.line'
    _rec_name = 'ref_int'

    fair_id = fields.Many2one('virtual.fair', string='Fair')
    facturation = fields.Char('Facturation')
    ref_int = fields.Char('Ref Int')
    customer_type = fields.Char('Custopmer Type')
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
