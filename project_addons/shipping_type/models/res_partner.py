# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


DEFAULT_SHIPPING_TYPE = ''
STRING_SHIPPING_TYPE = 'Transporte'
HELP_SHIPPING_TYPE = 'Tipo de envío: Pasaran, Agencia o en Ruta'
SHIPPING_TYPE_SEL =  [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')]


class InfoRouteMixin(models.AbstractModel):
    _name = 'info.route.mixin'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    info_route_str = fields.Char('Info route', compute='get_info_route')
    urgent = fields.Boolean('Urgent', help='Default urgent for partner orders\nPlus 3.20%')

    @api.onchange('associate')
    def _onchange_associate(self):
        super()._onchange_associate()
        if not self.associate:
            self.urgent = False


    def get_child_vals(self, vals):
        child_vals = {}
        if 'shipping_type' in vals:
            child_vals.update(shipping_type=vals['shipping_type'])
        if 'delivery_route_path_id' in vals:
            child_vals.update(delivery_route_path_id=vals['delivery_route_path_id'])
        if 'urgent' in vals:
            child_vals.update(urgent=vals['urgent'])
        if 'carrier_id' in vals and 'carrier_id' in self.fields_get_keys():
            child_vals.update(carrier_id=vals['carrier_id'])
        if 'campaign_id' in vals and 'campaign_id' in self.fields_get_keys():
            child_vals.update(campaign_id=vals['campaign_id'])
        return child_vals

    def update_info_route_vals(self):
        route_vals = {'shipping_type': self.shipping_type,
                      'delivery_route_path_id': self.delivery_route_path_id.id,
                      'urgent': self.urgent}
        if 'carrier_id' in self.fields_get_keys():
            route_vals['carrier_id'] = self.carrier_id and self.carrier_id.id
        if 'campaign_id' in self.fields_get_keys():
            route_vals['campaign_id'] = self.campaign_id and self.campaign_id.id
        return route_vals

    @api.multi
    def get_info_route(self):

        for obj in self:
            if obj.shipping_type or obj.delivery_route_path_id:
                if 'carrier_id' in obj.fields_get_keys():
                    carrier_id = obj.carrier_id and obj.carrier_id.name or '--'
                else:
                    carrier_id = '--'

                name2 = obj.delivery_route_path_id.name or 'Sin ruta' if obj.shipping_type != 'agency' else carrier_id
                name = '* ' if obj.urgent else ''
                shipping_type = obj._fields['shipping_type'].convert_to_export(obj.shipping_type, obj) if obj.shipping_type else 'Sin envío'
                obj.info_route_str = '{}{}: {}'.format(name, shipping_type, name2)
            else:
                obj.info_route_str = False


class ResPartner(models.Model):

    _inherit = ['res.partner', 'info.route.mixin']
    _name = 'res.partner'

