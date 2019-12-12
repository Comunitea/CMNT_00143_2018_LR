# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    amount_pending_to_send = fields.Float(compute='_compute_amount_pending_to_send')

    def _compute_amount_pending_to_send(self):
        for partner in self:
            prices = self.env['stock.picking'].search([
                ('partner_id', 'child_of', partner.id),
                ('picking_type_id.code', '=', 'outgoing'),
                ('state', 'in', ('confirmed', 'assigned'))
            ]).mapped('move_line_ids.sale_price_total')
            partner.amount_pending_to_send = sum(prices)
