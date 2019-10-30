# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class SaleInvoiceOnDate(models.TransientModel):

    _name = "sale.invoice.on.date"

    invoice_until_date = fields.Date()

    def view_invoiceable_orders(self):
        batchs = self.env["stock.batch.picking"].search(
            [
                ("invoiced", "!=", True),
                ("date_done", "<", self.invoice_until_date),
                ("picking_type_id.code", "=", "outgoing")
            ]
        )
        invoiceable_sales = batchs.mapped("sale_ids")
        action = self.env.ref("sale.action_orders").read()[0]
        action["domain"] = [('id', 'in', invoiceable_sales._ids)]
        return action
