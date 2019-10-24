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


    @api.multi
    @api.constrains('shipping_type', 'delivery_route_path_id', 'payment_term_id', 'picking_type_id')
    def _check_delivery_info(self):
        return
        for batch in self.filtered(lambda x: x.picking_type_id.code=='outgoing'):
            if not batch.shipping_type:
                raise ValidationError(_('Información de envío incompleta'))
            if not batch.shipping_type or \
                    (batch.shipping_type == 'route' and not batch.delivery_route_path_id):
                raise ValidationError(_('Información de envío incompleta'))
            #if not batch.payment_term_id:
            #    raise ValidationError(_('Información de plazos de pago incompleta'))

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

    def check_allow_change_route_fields(self):
        if any(move.state == 'done' for move in self.move_lines):
            raise ValidationError(_('No puedes cambiar en movimientos ya realizados'))
        return True


    @api.multi
    def write(self, vals):
        return super().write(vals)

