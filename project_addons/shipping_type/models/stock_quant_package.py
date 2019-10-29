# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def _count_move_line_ids(self):
        for pack in self:
            pack.count_move_line = len(pack.move_line_ids)

    count_move_line = fields.Integer(compute=_count_move_line_ids)
    picking_ids = fields.One2many('stock.picking', compute='get_stock_pickings')

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", compute='compute_route_fields', inverse='set_route_fields')
    campaign_id = fields.Many2one('campaign', 'Campaign')
    #shipping_type = fields.Selection(compute='compute_route_fields', inverse='set_route_fields')
    #delivery_route_path_id = fields.Many2one(compute='compute_route_fields', inverse='set_route_fields')
    payment_term_id = fields.Many2one(compute='compute_route_fields', inverse='set_route_fields')
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE, compute='compute_route_fields', inverse='set_route_fields')
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de transporte", compute='compute_route_fields', inverse='set_route_fields')
    info_route_str = fields.Char('Info ruta', compute='compute_route_fields')

    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago', compute='compute_route_fields', inverse='set_route_fields')

    @api.multi
    def get_info_route(self):
        for obj in self:
            if obj.shipping_type == 'pasaran':
                name = 'Pasarán'
            elif obj.shipping_type == 'urgent':
                name = 'Urgente'
                if 'carrier_id' in obj.fields_get_keys() and obj.carrier_id:
                    name = '{}: {}'.format(name, obj.carrier_id.name)

            elif obj.shipping_type == 'route':
                name = 'Ruta: {}'.format(obj.delivery_route_path_id and obj.delivery_route_path_id.name)
            else:
                name = 'No definido'
            return '{} / {}'.format(name, obj.payment_term_id and obj.payment_term_id.display_name or '')


    @api.multi
    def compute_route_fields(self):
        for pack in self.sudo():
            domain = [('result_package_id', '=', pack.id)]
            moves = self.env['stock.move.line'].search(domain).mapped('move_id')
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
                    print (pack.shipping_type)
                delivery_route_path_ids = moves.mapped('delivery_route_path_id')
                if len(delivery_route_path_ids) == 1:
                    pack.delivery_route_path_id = delivery_route_path_ids[0]
                carrier_ids = moves.mapped('carrier_id')
                if len(carrier_ids) == 1:
                    pack.carrier_id = carrier_ids[0]
                payment_term_id = moves.mapped('payment_term_id')
                if len(payment_term_id) == 1:
                    pack.payment_term_id = payment_term_id
                pack.info_route_str = pack.get_info_route()

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
        return

    def propagate_route_vals(self, vals):
        return True

    @api.multi
    def write(self, vals):
        return super().write(vals)







