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

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        for batch in self:
            batch.picking_ids.write({'carrier_id': batch.carrier_id.id})

    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        for batch in self:
            batch.picking_ids.write({'shipping_type': batch.shipping_type})

    @api.onchange('delivery_route_path_id')
    def onchange_delivery_route_path_id(self):
        for batch in self:
            batch.picking_ids.write({'delivery_route_path_id': batch.delivery_route_path_id.id})

    @api.multi
    def write(self, vals):

        child_vals = self.get_write_route_vals(vals)
        if child_vals:
            ctx = self._context.copy()
            ctx.update(write_from_pick=True)
            self.mapped('picking_ids').with_context(ctx).write(child_vals)
        return super().write(vals)

