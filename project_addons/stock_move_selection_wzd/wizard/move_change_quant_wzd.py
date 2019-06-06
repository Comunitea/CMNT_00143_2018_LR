# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockQuant(models.Model):

    _inherit ='stock.quant'

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        return super()._gather(product_id=product_id, location_id=location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)



class ChangeQuantWzd(models.TransientModel):
    _name = 'change.quant.wzd'

    wzd_id = fields.Many2one('move.change.quant.wzd')


    selection = fields.Boolean('Selección')
    sequence = fields.Integer("Sequence", defaul = 50)
    quant_id = fields.Many2one('stock.quant')
    location_id = fields.Many2one('stock.location', 'Origen')
    package_id = fields.Many2one('stock.quant.package', 'Paquete')
    lot_id = fields.Many2one('stock.production.lot', 'Lote')
    quantity = fields.Float('Cantidad disponible')
    reserved_quantity = fields.Float('Cantidad reservada')
    new_quantity = fields.Float('Cantidad')


class MoveChangeQuantWzd(models.TransientModel):
    """Create a stock.batch.picking from stock.picking
    """

    _name = 'move.change.quant.wzd'
    _description = 'Asistente para cambiar las reservas de almacén'
    _order = 'sequence'

    move_id = fields.Many2one('stock.move', 'Movimiento')
    state = fields.Selection(related="move_id.state")
    move_line_ids= fields.One2many(related="move_id.move_line_ids", string='Stock seleccionado')
    quant_ids = fields.Many2many('change.quant.wzd', string='Stock disponibles')

    def _prepare_quant(self, quant):
        return {'quant_id': quant.id,
                'selection': False,
                'location_id': quant.location_id.id,
                'package_id': quant.package_id.id,
                'lot_id': quant.lot_id.id,
                'quantity': quant.quantity,
                'reserved_quantity': quant.reserved_quantity
                                }

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        move = self._context.get('active_id', False)
        move_id = self.env['stock.move'].browse(move)
        warehouse_id = move_id.picking_type_id.warehouse_id
        location_id = warehouse_id.lot_stock_id
        quants = self.env['stock.quant']._gather(product_id=move_id.product_id, location_id=location_id)

        defaults['quant_ids'] = [(0, 0, self._prepare_quant(x)) for x in quants]
        defaults['move_id'] = move
        return defaults


    def action_apply_quant(self):
        self.move_id.do_unreserve_for_pda()
        route_vals = self.move_id.update_info_route_vals()
        moves = self.env['stock.move']
        for quant in self.quant_ids.filtered(lambda x: x.new_quantity>0.00):
            new_move_id = self.move_id._split(quant.new_quantity)
            new_move = self.env['stock.move'].browse(new_move_id)
            vals = route_vals.copy()
            vals.update(location_id=quant.quant_id.location_id.id)
            new_move.write(vals)
            new_move.check_new_location()
            moves |= new_move

        if self.move_id not in moves:
            self.move_id.action_cancel_for_pda()

        moves._action_assign()
        return self.env['stock.picking.type'].return_action_show_moves(domain=[('id', 'in', moves.ids)])



