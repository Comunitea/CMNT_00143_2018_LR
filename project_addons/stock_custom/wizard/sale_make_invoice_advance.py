# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        """
            No viene la fecha en contexto, solo en el active_domain,
            por lo que necesitamos volver a ponerla en contexto
        """
        until_date = False
        if self._context.get("active_domain"):
            for domain in self._context["active_domain"]:
                if domain[0] == "invoice_until":
                    until_date = domain[2]
        sale_order_ids = self._context.get("active_ids", [])
        grouped_sales = self.env["sale.order"].read_group(
            [("id", "in", sale_order_ids)],
            ["partner_shipping_id", "payment_term_id"],
            ["partner_shipping_id", "payment_term_id"],
            lazy=False,
        )
        for sale_group_vals in grouped_sales:
            payment_term_id = sale_group_vals["payment_term_id"] and sale_group_vals["payment_term_id"][0] or False
            sale_orders = self.env["sale.order"].search(
                [
                    ("id", "in", sale_order_ids),
                    (
                        "payment_term_id",
                        "=", payment_term_id,
                    ),
                    (
                        "partner_shipping_id",
                        "=",
                        sale_group_vals["partner_shipping_id"][0],
                    ),
                ]
            )
            sale_pickings = sale_orders.mapped("batch_picking_ids.id")
            batchs = self.env["stock.batch.picking"].search(
                [
                    ("invoiced", "!=", True),
                    ("date_done", "<", until_date),
                    ("picking_type_id.code", "=", "outgoing"),
                    ("id", "in", sale_pickings),
                ]
            )
            batchs.create_invoice()
        if self._context.get("open_invoices", False):
            sale_orders = self.env["sale.order"].browse(sale_order_ids)
            return sale_orders.action_view_invoice()
        return {"type": "ir.actions.act_window_close"}
