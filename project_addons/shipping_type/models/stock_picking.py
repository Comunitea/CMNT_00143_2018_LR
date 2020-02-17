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
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.multi
    def write(self, vals):
        return super().write(vals)
        # res = super().write(vals)
        # r_vals = ['payment_term_id', 'shipping_type', 'delivery_route_path_id', 'carrier_id', 'campaign_id']
        # vals = list(set([x for x in vals.keys()]) & set(r_vals))
        # if not vals:
        #     return res
        # ctx = self._context.copy()
        # ctx.update(from_parent=True)
        # for obj in self:
        #     if obj.state == 'done':
        #         raise ValidationError(_('No puedes hacer cambiar estos valores en ordenes ya realizadas'))
        #
        #     domain = [('picking_id', '=', obj.id), ('result_package_id', '=', False)]
        #     move_ids = self.env['stock.move.line'].search(domain).mapped('move_id')
        #
        #     domain = [('picking_id', '=', obj.id), ('result_package_id', '!=', False)]
        #     package_ids = self.env['stock.move.line'].search(domain).mapped('result_package_id')
        #
        #     if not self._context.get('from_parent', False):
        #         ## Si no viene de una orden de carga, entonces ....
        #         if move_ids:
        #             if any(x in ('done', 'cancel') for x in move_ids.mapped('state')):
        #                 raise ValidationError(_('No puedes hacer cambiar estos valores en movimientos ya realizados'))
        #             if obj.batch_picking_id:
        #                 raise ValidationError(_('No puedes hacer cambiar estos valores en ordenes ya albaranadas'))
        #
        #     package_ids.with_context(ctx).write(obj.update_info_route_vals())
        #     move_ids.with_context(ctx).write(obj.update_info_route_vals())
        #
        # return res


