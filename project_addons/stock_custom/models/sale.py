# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def create_service_invoice_lines(self, invoice):
        for sale in self:
            for line in sale.order_line.filtered(
                lambda r: r.product_id.type == "service"
            ):
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoice.id, line.qty_to_invoice)

