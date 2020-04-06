# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    xls_imported = fields.Boolean()
    ecotasa = fields.Float()
    uom_factor = fields.Integer()
    uos_factor = fields.Integer()
    brand_partner = fields.Many2one('res.partner')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "active" in vals and not vals.get("active"):
            res.with_context(active_test=False).mapped(
                "product_variant_ids"
            ).write({"active": vals.get("active")})
        return res
