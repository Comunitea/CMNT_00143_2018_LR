# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError,ValidationError
from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE, HELP_SHIPPING_TYPE


class StockBatchPicking(models.Model):

    _inherit = 'stock.batch.picking'

    @api.multi
    def add_more_orders(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_to_orders_action').read()[0]
        domain = [('batch_delivery_id', '=', False), ('state', '=', 'assigned'), ('picking_type_id', '=', self.picking_type_id.id)]
        if self.delivery_route_path_ids:
            domain  += [('delivery_route_path_id', 'in', self.delivery_route_path_ids.ids)]
        if self.shipping_type:
            domain += [('shipping_type', '=', self.shipping_type)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]

        action['domain'] = domain
        self.env['stock.picking'].search(domain).write({'to_batch': self.id})
        ctx = self._context.copy()
        ctx.update(eval(action['context']))
        ctx.update(default_batch_picking_id=self.id)
        action['name'] = "Grupo: {}".format(self.name)
        action['display_name'] = "Grupo: {}".format(self.name)
        action['context'] = ctx
        return action


    @api.multi
    def add_more_moves(self):
        self.ensure_one()
        action = self.env.ref('stock_move_selection_wzd.stock_move_to_orders_action').read()[0]
        domain = [('batch_picking_id', '=', False), ('state', '=', 'assigned'), ('picking_type_id', '=', self.picking_type_id.id)]

        if self.delivery_route_path_ids:
            domain += [('delivery_route_path_id', 'in', self.delivery_route_path_ids.ids)]
        if self.shipping_type:
            domain += [('shipping_type', '=', self.shipping_type)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        if self.payment_term_ids:
            domain += [('payment_term_id', 'in', self.payment_term_ids.ids)]

        action['domain'] = domain
        self.env['stock.picking'].search(domain).write({'to_batch': self.id})
        ctx = self._context.copy()
        ctx.update(eval(action['context']))
        ctx.update(default_batch_picking_id=self.id)
        name = self.picking_type_id.batch_name
        action['name'] = "{} : {}".format(name, self.name)
        action['display_name'] ="{} : {}".format(name, self.name)
        action['context'] = ctx
        return action

