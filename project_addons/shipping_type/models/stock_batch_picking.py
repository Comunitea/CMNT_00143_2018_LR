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
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", compute='compute_route_fields',
                                 inverse='set_route_fields')
    shipping_type = fields.Selection(compute='compute_route_fields', inverse='set_route_fields', store=True)
    delivery_route_path_id = fields.Many2one('delivery.route.path', compute='compute_route_fields',
                                             inverse='set_route_fields', store=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago', compute='compute_route_fields',
                                      inverse='set_route_fields', store=True)

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

    def check_allow_change_route_fields(self):
        if any(move.state == 'done' for move in self.move_lines):
            raise ValidationError(_('No puedes cambiar en movimientos ya realizados'))
        return True

    @api.multi
    def set_route_fields(self):
        for pick in self:
            pick.check_allow_change_route_fields()
            moves = pick.move_lines
            vals = {}
            if pick.shipping_type:
                vals.update({'shipping_type': pick.shipping_type})
            if pick.delivery_route_path_id:
                vals.update({'delivery_route_path_id': pick.delivery_route_path_id.id})
            if pick.carrier_id:
                vals.update({'carrier_id': pick.carrier_id.id})
            if pick.payment_term_id:
                vals.update({'payment_term_id': pick.payment_term_id.id})
            moves.write(vals)

    @api.multi
    @api.constrains('shipping_type', 'delivery_route_path_id', 'payment_term_id', 'picking_type_id')
    def _check_delivery_info(self):
        return

    @api.multi
    def write(self, vals):
        return super().write(vals)

