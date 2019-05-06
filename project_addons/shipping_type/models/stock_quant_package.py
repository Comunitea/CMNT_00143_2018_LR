# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    dest_partner_id = fields.Many2one("res.partner")
    delivery_carrier_id = fields.Many2one("delivery.carrier")
    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado."
    )
    partner_default_shipping_type = fields.Selection(related="dest_partner_id.default_shipping_type")