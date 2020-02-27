# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockBatchPicking(models.Model):

    _inherit = ['stock.batch.picking', 'info.route.mixin']
    _name = 'stock.batch.picking'

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de albarán', required=True, readonly=False)
    usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage')


    @api.multi
    def write(self, vals):
        return super().write(vals)

