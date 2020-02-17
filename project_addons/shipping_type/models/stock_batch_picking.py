# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockBatchPicking(models.Model):

    _inherit = ['stock.batch.picking', 'info.route.mixin']
    _name = 'stock.batch.picking'

    campaign_id = fields.Many2one('campaign', 'Campaign')
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.multi
    @api.constrains('shipping_type', 'delivery_route_path_id', 'payment_term_id', 'picking_type_id')
    def _check_delivery_info(self):
        return

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
        #     picking_ids = obj.picking_ids
        #     if not self._context.get('from_parent', False):
        #         ## Si no viene de una orden de carga, entonces ....
        #         if any(x in ('done', 'cancel') for x in obj.picking_ids.mapped('state')):
        #             raise ValidationError(_('No puedes hacer cambiar estos valores con picks ya realizados'))
        #         if obj.batch_delivery_id:
        #             raise ValidationError(_('No puedes hacer cambiar estos valores en albaranes con una orden de carga'))
        #     picking_ids.with_context(ctx).write(obj.update_info_route_vals())
        # return res
