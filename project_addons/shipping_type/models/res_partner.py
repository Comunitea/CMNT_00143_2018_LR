# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


DEFAULT_SHIPPING_TYPE = ''
STRING_SHIPPING_TYPE = 'Tipo de envío'
HELP_SHIPPING_TYPE = 'Tipo de envío: Pasaran, Agencia o en Ruta'
SHIPPING_TYPE_SEL =  [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)

    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")