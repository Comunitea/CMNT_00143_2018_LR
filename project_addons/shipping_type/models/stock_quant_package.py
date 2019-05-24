# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    dest_partner_id = fields.Many2one("res.partner")
    delivery_carrier_id = fields.Many2one("delivery.carrier")
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE, help=HELP_SHIPPING_TYPE)
    partner_shipping_type = fields.Selection(related="dest_partner_id.shipping_type")