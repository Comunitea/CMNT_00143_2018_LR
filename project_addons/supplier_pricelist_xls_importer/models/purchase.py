# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.product_id.active and res.product_id.xls_imported:
            res.product_id.active = True
            res.product_id.product_tmpl_id.active = True
        return res

    def write(self, vals):
        res = super().write(vals)
        for line in self:
            if not line.product_id.active and line.product_id.xls_imported:
                line.product_id.active = True
                line.product_id.product_tmpl_id.active = True
        return res
