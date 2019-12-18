# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockPicking(models.Model):

    _inherit = ['stock.picking', 'info.route.mixin']
    _name = 'stock.picking'

    campaign_id = fields.Many2one('campaign', 'Campaign')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.multi
    def compute_route_fields(self):
        for pick in self:
            moves = pick.move_lines
            if moves:
                shipping_type_ids = []
                for move in moves:
                    if move.shipping_type in shipping_type_ids:
                        continue
                    shipping_type_ids.append(move.shipping_type)
                if shipping_type_ids[0] and len(shipping_type_ids) == 1:
                    pick.shipping_type = shipping_type_ids[0]
                delivery_route_path_ids = moves.mapped('delivery_route_path_id')
                if len(delivery_route_path_ids) == 1:
                    pick.delivery_route_path_id = delivery_route_path_ids[0]
                carrier_ids = moves.mapped('carrier_id')
                if len(carrier_ids) == 1:
                    pick.carrier_id = carrier_ids[0]
                payment_term_ids = moves.mapped('payment_term_id')
                if len(payment_term_ids) == 1:
                    pick.payment_term_id = payment_term_ids[0]
    @api.multi
    def write(self, vals):
        return super().write(vals)

