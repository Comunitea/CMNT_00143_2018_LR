# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def split_if_moves(self, batch_picking_id, moves):
        backorder_ids = self.env['stock.picking']
        if not moves:
            return
        for picking in self:
            backorder_picking = picking.copy({
                'name': '/',
                'move_lines': [],
                'move_line_ids': [],
                'backorder_id': picking.id,
            })
            picking.message_post(
                _(
                    'Se dividido en <a href="#" '
                    'data-oe-model="stock.picking" '
                    'data-oe-id="%d">%s</a> desde por la expedición. {}'
                ) % (
                    backorder_picking.id,
                    backorder_picking.name,
                    batch_picking_id.name
                )
            )
            moves.write({
                'picking_id': backorder_picking.id,
            })
            moves.mapped('move_line_ids').write({
                'picking_id': backorder_picking.id,
            })
            backorder_ids |= backorder_picking
        return backorder_ids
