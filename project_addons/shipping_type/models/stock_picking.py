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
    #carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    #delivery_route_path_id = fields.Many2one(related="batch_picking_id.delivery_route_path_id")
    #shipping_type = fields.Selection(related="batch_picking_id.shipping_type")
    #payment_term_id = fields.Many2one(related="batch_picking_id.payment_term_id")

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        return res



