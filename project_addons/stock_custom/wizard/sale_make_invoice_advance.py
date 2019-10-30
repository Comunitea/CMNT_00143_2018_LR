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
        sale_orders = self.env["sale.order"].browse(
            self._context.get("active_ids", [])
        )
        sale_orders.mapped("batch_picking_ids").filtered(
            lambda r: not r.invoiced
            and r.state == "done"
            and r.picking_type_id.code == "outgoing"
        ).create_invoice()
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
