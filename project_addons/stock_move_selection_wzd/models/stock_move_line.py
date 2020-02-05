# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import SGA_STATES

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sga_integrated = fields.Boolean(related='move_id.picking_type_id.sga_integrated')
    sga_state = fields.Selection(related='move_id.sga_state', store=True)
    batch_picking_id = fields.Many2one(related='picking_id.batch_picking_id')
    batch_delivery_id = fields.Many2one(related='picking_id.batch_delivery_id')

    @api.constrains('result_package_id', 'partner_id')
    def check_partner(self):
        import ipdb; ipdb.set_trace()
        for line in self.filtered(lambda x: x.move_id.picking_type_id.group_code.code =='outgoing'):
            if not line.result_package_id:
                continue
            partner_ids = line.result_package_id.mapped('move_line_ids').mapped('partner_id')
            if partner_ids and len(partner_ids)!= 1 or partner_ids != line.partner_id:
                raise ValueError(_('No es posible empaquetar para distintos clientes en las operaciones de salida'))

    @api.multi
    def write(self, vals):
        if 'result_package_id' in vals:
            result_package_id = self.env['stock.quant.package'].browse(vals.get('result_package_id'))

        return super().write(vals)

    @api.multi
    def unpack(self):
        for move in self:
            if move.state != 'done':
                move.write({'result_package_id': False})
            elif move.package_id and move.state in ('assigned', 'partially_available') and move.product_qty != 0:
                move.package_id.mapped('quant_ids').write({'package_id': False})
                move.write({'package_id': False})
        return True

    @api.multi
    def _set_quantity_done(self, quantity):
        for line in self:
            line.update({
                'qty_done': quantity
            })

    @api.multi
    def split_move_reserved_qty(self, qty=0):
        moves = []
        self.ensure_one()
        for move_line in self:
            move = move_line.move_id
            qty = move.product_uom_qty - move.reserved_availability
        moves.append(move._split(qty=qty))
        moves.append(move.id)
        return self.env['stock.picking.type'].return_action_show_moves(domain=[('id', 'in', moves)])
