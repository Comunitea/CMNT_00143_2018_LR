# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockBatchPicking(models.Model):

    _inherit = ['stock.batch.picking', 'info.route.mixin']
    _name = 'stock.batch.picking'

    campaign_id = fields.Many2one('campaign', 'Campaign')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    #shipping_type = fields.Selection(compute='compute_route_fields', inverse='set_route_fields')
    #delivery_route_path_id = fields.Many2one('delivery.route.path', compute='compute_route_fields',
    #                                         inverse='set_route_fields')

    @api.multi
    def set_route_fields(self):
        for batch in self:
            batch.check_allow_change_route_fields()
            moves = batch.move_lines
            moves.write({
                'shipping_type': batch.shipping_type,
                'delivery_route_path_id': batch.delivery_route_path_id.id,
                'carrier_id': batch.carrier_id.id
            })

    @api.multi
    @api.depends('move_lines.shipping_type', 'move_lines.delivery_route_path_id', 'move_lines.carrier_id')
    def compute_route_fields(self):
        for batch in self:
            moves = batch.move_lines
            # if any(move.state == 'done' for move in moves):
            #    raise ValidationError (_('No puedes cambiar en movimientos ya realizados'))
            if moves:
                shipping_type_ids = []
                for move in moves:
                    if move.shipping_type in shipping_type_ids:
                        continue
                    shipping_type_ids.append(move.shipping_type)
                if shipping_type_ids[0] and len(shipping_type_ids) == 1:
                    batch.shipping_type = shipping_type_ids[0]
                delivery_route_path_ids = moves.mapped('delivery_route_path_id')
                if len(delivery_route_path_ids) == 1:
                    batch.delivery_route_path_id = delivery_route_path_ids[0]
                carrier_ids = moves.mapped('carrier_id')
                if len(carrier_ids) == 1:
                    batch.carrier_id = carrier_ids[0]

    def check_allow_change_route_fields(self):
        if any(move.state == 'done' for move in self.move_lines):
            raise ValidationError(_('No puedes cambiar en movimientos ya realizados'))
        return True


    @api.multi
    def write(self, vals):
        return super().write(vals)

