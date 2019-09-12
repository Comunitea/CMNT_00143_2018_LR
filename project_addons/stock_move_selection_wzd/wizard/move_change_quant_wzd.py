# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError
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


    @api.onchange('new_quantity')
    def onchange_new_qty(self):

        total_qty = sum(x.new_quantity for x in self.wzd_id.quant_ids)
        if not self.wzd_id.override_qty and total_qty != self.wzd_id.move_id.product_uom_qty:
            raise ValidationError (_('No se permite variar la cantidad total del movimiento'))
        if self.new_quantity > self.quantity:
            raise ValidationError(_('No puedes reservar más cantidad que la disponible ne la ubicación'))


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
    override_qty = fields.Boolean('Permite cambiar cantidad total', default=False)
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


    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)

        return vals

    def action_apply_quant(self):

        precision_digits = self.env[
            'decimal.precision'].precision_get('Product Unit of Measure')
        self.move_id.do_unreserve_for_pda()
        route_vals = self.move_id.update_info_route_vals()
        moves = self.env['stock.move']
        for quant_id in self.quant_ids.filtered(lambda x: x.new_quantity>0.00):
            quant = quant_id.quant_id
            ##SI CAMBIA EL PICKING_TYPE_ID DEL MOVMIMIENTOS SEGÚN LA NUEVA UBICACION
            if self.move_id.picking_type_id.code == 'incoming':
                field = 'location_dest_id'
            else:
                field = 'location_id'

            new_location = quant.location_id
            if new_location.picking_type_id and new_location.picking_type_id != self.move_id.location_id.picking_type_id:
                new_move_id = self.move_id._split(quant_id.new_quantity)
                new_move = self.env['stock.move'].browse(new_move_id)
                ##tengo que cambiarlod e albarán
                new_loc_vals = {
                    field: new_location.id,
                    'picking_type_id': new_location.picking_type_id.id,
                    'picking_id': False
                }
                new_loc_vals.update(route_vals)
                new_move.write(new_loc_vals)
                new_move.check_new_location()
                if float_compare(quant_id.new_quantity, 0.0, precision_digits=precision_digits) > 0:
                    available_quantity = quant._get_available_quantity(
                    new_move.product_id, quant[field], lot_id=quant.lot_id,
                    package_id=quant.package_id, owner_id=quant.owner_id,
                    )
                if float_compare(
                    available_quantity, 0.0, precision_digits=precision_digits) <= 0:
                    return
                new_move._update_reserved_quantity(
                    quant_id.new_quantity, available_quantity, quant[field],
                    lot_id=quant.lot_id, package_id=quant.package_id,
                    owner_id=quant.owner_id, strict=True
                )
                moves |= new_move
            else:
                if float_compare(quant_id.new_quantity, 0.0, precision_digits=precision_digits) > 0:
                    available_quantity = quant._get_available_quantity(
                    new_move.product_id, quant[field], lot_id=quant.lot_id,
                    package_id=quant.package_id, owner_id=quant.owner_id,
                    )
                if float_compare(
                    available_quantity, 0.0, precision_digits=precision_digits) <= 0:
                    return
                new_move._update_reserved_quantity(
                    quant_id.new_quantity, available_quantity, quant[field],
                    lot_id=quant.lot_id, package_id=quant.package_id,
                    owner_id=quant.owner_id, strict=True
                )
                moves |= new_move
        if moves and self.move_id not in moves:
            self.move_id.action_cancel_for_pda()

        moves._action_assign()
        moves.move_sel_assign_picking()
        return self.env['stock.picking.type'].return_action_show_moves(domain=[('id', 'in', moves.ids)])



