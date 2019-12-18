# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import pycompat

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reservation_days = fields.Integer (related='partner_id.reservation_days')


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    split_moves = fields.Boolean('Split moves', default=True)
    hide_split_moves = fields.Boolean('Hide split moves', compute='compute_split_moves')


    @api.multi
    def compute_split_moves(self):
        for line in self:
            line.hide_split_moves = line.product_id.type != 'product' or line.product_id.qty_available > line.product_uom_qty

    @api.multi
    def alternate_split_moves(self):
        for line in self:
            line.split_moves = not line.split_moves

    def get_moves_to_split(self):
        return self.filtered(lambda x:x.split_moves).mapped('move_ids').filtered(lambda x: x.state == 'partially_available')

    @api.multi
    def _action_launch_procurement_rule(self):
        super()._action_launch_procurement_rule()
        moves = self.get_moves_to_split()
        for move in moves:
            new_move = move._split(move.product_uom_qty - move.reserved_availability)
            new_move = move.browse(new_move)
            if new_move.picking_type_id != move.picking_type_id:
                new_move._assign_picking()
        return True

