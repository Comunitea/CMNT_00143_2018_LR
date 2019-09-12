# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = ['stock.quant.package', 'info.route.mixin']
    _name = 'stock.quant.package'

    @api.multi
    def _count_move_line_ids(self):
        for pack in self:
            pack.count_move_line = len(pack.move_line_ids)


    partner_shipping_type = fields.Char('')
    count_move_line = fields.Integer(compute=_count_move_line_ids)
    picking_ids = fields.One2many('stock.picking', compute='get_stock_pickings')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.multi
    def get_stock_pickings(self):
        for pack in self:
            pack.picking_ids = self.env['stock.move.line'].search([('result_package_id','=', pack.id)]).mapped('picking_id')

    def propagate_route_vals(self, vals):
        ctx = self._context.copy()
        ctx.update(write_from_picking=True)
        child_vals = self.get_write_route_vals(vals)
        move_vals = {}
        if child_vals:
            move_vals.update(child_vals)
            self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)
        return True

    @api.multi
    def write(self, vals):

        if self._context.get('no_propagate_route_vals', True):
            self.propagate_route_vals(vals)
        super().write(vals)






