# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Productsupplierinfo(models.Model):

    _inherit = 'product.supplierinfo'

    xls_imported = fields.Boolean()
    supplier_discount_group_id = fields.Many2one('supplier.discount.group')
    log_id = fields.Many2one("log.import.spl", required=True)
    active = fields.Boolean(related='product_id.active', store=True)
