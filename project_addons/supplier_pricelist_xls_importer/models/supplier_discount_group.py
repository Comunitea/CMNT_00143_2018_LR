# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SupplierDiscountGroup(models.Model):

    _name = 'supplier.discount.group'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Supplier')
    discount = fields.Float('Discount (%)')

    _sql_constraints = [
        ('name_partner_unique', 'unique(name, partner_id)', 'Discount group names must be unique !'),
    ]
