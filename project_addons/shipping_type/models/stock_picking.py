# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    #bool_shipping_type = fields.Boolean('Agrupa por tipo de envío')
    #bool_delivery_route_path_id = fields.Boolean('Agrupa por ruta de transporte')
    #bool_carrier_id = fields.Boolean('Agrupa por forma de envío')
    #bool_campaign_id = fields.Boolean('Agrupa por campaña')


class StockBatchPicking(models.Model):

    _inherit = ['stock.batch.picking', 'info.route.mixin']
    _name = 'stock.batch.picking'

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        for batch in self:
            batch.picking_ids.write({'carrier_id': batch.carrier_id.id})

    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        for batch in self:
            batch.picking_ids.write({'shipping_type': batch.shipping_type})

    @api.onchange('delivery_route_path_id')
    def onchange_delivery_route_path_id(self):
        for batch in self:
            batch.picking_ids.write({'delivery_route_path_id': batch.delivery_route_path_id.id})


# class StockPicking(models.Model):
#
#     _inherit = ['stock.picking', 'info.route.mixin']
#     _name = 'stock.picking'
#
#     def get_new_vals(self):
#         vals = self.update_info_route_vals()
#         return vals
#
#     @api.multi
#     def write(self, vals):
#
#         if self._context.get('no_propagate_route_vals', True):
#             child_vals = self.get_write_route_vals(vals)
#             if child_vals and not self._context.get('write_from_pick', False):
#                 for pick in self:
#                     if pick.batch_picking_id:
#                         raise ValidationError ('No puedes cambiar estos valores en el albarán si ya está en una carta de porte')
#             if child_vals:
#                 ctx = self._context.copy()
#                 ctx.update(write_from_pick=True)
#                 packages = self.move_line_ids.mapped('result_package_id')
#                 if packages:
#                     packages.with_context(ctx).write(child_vals)
#                 moves = self.move_line_ids.filtered(lambda x: not x.result_package_id).mapped('move_id')
#                 if moves:
#                     moves.with_context(ctx).write(child_vals)
#         super().write(vals)

