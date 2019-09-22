# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = ['stock.quant.package', 'info.route.mixin']
    _name = 'stock.quant.package'

    @api.multi
    def _count_move_line_ids(self):
        for pack in self:
            pack.count_move_line = len(pack.move_line_ids)

    count_move_line = fields.Integer(compute=_count_move_line_ids)
    picking_ids = fields.One2many('stock.picking', compute='get_stock_pickings')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')
    shipping_type = fields.Selection(compute='compute_route_fields', inverse='set_route_fields')
    delivery_route_path_id = fields.Many2one('delivery.route.path', compute='compute_route_fields', inverse='set_route_fields')


    @api.multi
    @api.depends('move_line_ids')
    def compute_route_fields(self):

        for pack in self:
            moves = pack.move_line_ids.mapped('move_id')
            #if any(move.state == 'done' for move in moves):
            #    raise ValidationError (_('No puedes cambiar en movimientos ya realizados'))
            if moves:
                shipping_type_ids = []
                for move in moves:
                    if move.shipping_type in shipping_type_ids:
                        continue
                    shipping_type_ids.append(move.shipping_type)
                if shipping_type_ids[0] and len(shipping_type_ids) == 1:
                    pack.shipping_type = shipping_type_ids[0]
                delivery_route_path_ids = moves.mapped('delivery_route_path_id')
                if len(delivery_route_path_ids) == 1:
                    pack.delivery_route_path_id = delivery_route_path_ids[0]

                carrier_ids = moves.mapped('carrier_id')
                if len(carrier_ids) == 1:
                    pack.carrier_id = carrier_ids[0]

    def check_allow_change_route_fields(self):
        if any(move.state == 'done' for move in self.move_line_ids):
            raise ValidationError (_('No puedes cambiar en movimientos ya realizados'))
        return True

    @api.multi
    def set_route_fields(self):
        for pack in self:
            pack.check_allow_change_route_fields()
            moves = pack.move_line_ids.mapped('move_id')
            moves.write({
                'shipping_type': pack.shipping_type,
                'delivery_route_path_id': pack.delivery_route_path_id.id,
                'carrier_id': pack.carrier_id.id
            })

    @api.multi
    def get_stock_pickings(self):
        for pack in self:
            pack.picking_ids = self.env['stock.move.line'].search([('result_package_id','=', pack.id)]).mapped('picking_id')

    def propagate_route_vals(self, vals):
        return True
        ctx = self._context.copy()
        ctx.update(write_from_picking=True)
        child_vals = self.get_write_route_vals(vals)
        move_vals = {}
        if child_vals:
            move_vals.update(child_vals)
            self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)
        return True

    @api.multi
    def write(self, vals):
        return super().write(vals)
        if self._context.get('no_propagate_route_vals', True):
            self.propagate_route_vals(vals)
        super().write(vals)






