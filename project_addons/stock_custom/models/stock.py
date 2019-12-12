# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields
from datetime import date


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    computed_discount = fields.Float(compute="_compute_computed_discount")

    def _compute_computed_discount(self):
        for line in self:
            discount = line.sale_discount
            discount -= line.move_id.company_id.get_discount_decrease_shipping(
                line.batch_picking_id.shipping_type or line.shipping_type
            )
            if line.sale_line.order_id.financiable_payment:
                discount -= (
                    line.move_id.company_id.discount_decrease_financiable
                )
            line.computed_discount = discount

    @api.multi
    def _compute_sale_order_line_fields(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to sales orders (stricter warehouse users, inter-company
        records...).
        """
        for line in self:
            discount = line.computed_discount
            sale_line = line.sale_line
            price_unit = line.sale_price_unit * (1 - (discount or 0.0) / 100.0)
            taxes = line.sale_tax_id.compute_all(
                price_unit=price_unit,
                currency=line.currency_id,
                quantity=line.qty_done or line.product_qty,
                product=line.product_id,
                partner=sale_line.order_id.partner_shipping_id,
            )
            if sale_line.company_id.tax_calculation_rounding_method == (
                "round_globally"
            ):
                price_tax = sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])
                )
            else:
                price_tax = taxes["total_included"] - taxes["total_excluded"]
            line.update(
                {
                    "sale_tax_description": ", ".join(
                        t.name or t.description for t in line.sale_tax_id
                    ),
                    "sale_price_subtotal": taxes["total_excluded"],
                    "sale_price_tax": price_tax,
                    "sale_price_total": taxes["total_included"],
                }
            )
