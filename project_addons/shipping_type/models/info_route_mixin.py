# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

DEFAULT_SHIPPING_TYPE = ''
STRING_SHIPPING_TYPE = 'Transporte'
HELP_SHIPPING_TYPE = 'Tipo de envío: Pasaran, Agencia o en Ruta'
SHIPPING_TYPE_SEL =  [
    ('urgent', 'Urgente'),
    ('pasaran', 'Pasarán'),
    ('route', 'Ruta')]


class InfoRouteMixin(models.AbstractModel):
    _name = 'info.route.mixin'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de transporte")
    info_route_str = fields.Char('Info ruta', compute='get_info_route')
    urgent = fields.Boolean('Urgent', help='Default urgent for partner orders\nPlus 3.20%', compute='_partner_urgent')

    @api.multi
    def _partner_urgent(self):
        if 'partner_id' in self.fields_get_keys():
            for obj in self:
                obj.urgent = obj.partner_id.urgent
        else:
            self.write({'urgent': True})

    @api.multi
    def write(self, vals):
        return super().write(vals)

    def get_write_route_vals(self, vals):
        child_vals = {}
        if 'shipping_type' in vals:
            child_vals.update(shipping_type=vals['shipping_type'])
        if 'delivery_route_path_id' in vals:
            child_vals.update(delivery_route_path_id=vals['delivery_route_path_id'])
        if 'carrier_id' in vals and 'carrier_id' in self.fields_get_keys():
            child_vals.update(carrier_id=vals['carrier_id'])
        if 'campaign_id' in vals and 'campaign_id' in self.fields_get_keys():
            child_vals.update(campaign_id=vals['campaign_id'])

        return child_vals

    def update_info_route_vals(self):
        route_vals = {'shipping_type': self.shipping_type,
                      'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id,
                      }
        if 'carrier_id' in self.fields_get_keys() and self.carrier_id:
            route_vals['carrier_id'] = self.carrier_id.id
        if 'campaign_id' in self.fields_get_keys() and self.campaign_id:
            route_vals['campaign_id'] = self.campaign_id.id
        return route_vals

    @api.multi
    def get_info_route(self):
        for obj in self:
            if obj.shipping_type or obj.delivery_route_path_id:
                if 'carrier_id' in obj.fields_get_keys():
                    carrier_id = obj.carrier_id and obj.carrier_id.name or ''
                else:
                    carrier_id = ''

                name2 = '{} {}'.format(obj.delivery_route_path_id.name or 'Sin ruta', carrier_id)
                shipping_type = obj._fields['shipping_type'].convert_to_export(obj.shipping_type, obj) if obj.shipping_type else 'Sin envío'
                obj.info_route_str = '{}: {}'.format(shipping_type, name2)
            else:
                obj.info_route_str = False

