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

class ShippingType(models.Model):
    _name = 'shipping.type'

    code = fields.Char('Codigo')
    name = fields.Char('Nombre')

class InfoRouteMixin(models.AbstractModel):
    _name = 'info.route.mixin'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)

    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de transporte")
    info_route_str = fields.Char('Info ruta', compute='get_info_route')
    urgent = fields.Boolean('Urgent', help='Default urgent for partner orders\nPlus 3.20%', compute='_partner_urgent')
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago')

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

    def update_info_route_vals(self):

        child_vals = {}
        r_vals = ['payment_term_id',
                  'shipping_type',
                  'delivery_route_path_id',
                  'campaign_id']

        self_fields = self.fields_get_keys()
        for vl in list(set(r_vals) & set(self_fields)):
            if self[vl]:
                if self.fields_get()[vl]['type'] == 'many2one':
                    child_vals.update({vl: self[vl].id})
                else:
                    child_vals.update({vl: self[vl]})
        return child_vals

    @api.multi
    def get_info_route(self):

        for obj in self:

            if obj.shipping_type == 'pasaran':
                name = 'Pasarán'
            elif obj.shipping_type == 'urgent':
                name = 'Urgente'
            else:
                name = 'Ruta'
            if obj.delivery_route_path_id:
                name = '{}: {}'.format(name, obj.delivery_route_path_id.name)
            if 'carrier_id' in obj.fields_get_keys() and obj.carrier_id:
                name = '{} ({})'.format(name, obj.carrier_id.name)
            if obj.payment_term_id:
                name = '{} / {}'.format(name, obj.payment_term_id.display_name)
            obj.info_route_str = name
