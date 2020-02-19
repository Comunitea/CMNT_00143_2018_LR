# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def split_if_package(self, moves, delivery_id):
        backorder_ids = self.env['stock.picking']
        for picking in self:
            moves_to_split = moves.filtered(lambda x: x.picking_id == picking)
            if moves_to_split:
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
                        'data-oe-id="%d">%s</a> desde la orden de carga %s.'
                    ) % (
                        backorder_picking.id,
                        backorder_picking.name,
                        delivery_id.name
                    )
                )
                moves_to_split.write({
                    'picking_id': backorder_picking.id,
                })
                moves_to_split.mapped('move_line_ids').write({
                    'picking_id': backorder_picking.id,
                })
                backorder_ids |= backorder_picking

            picking.batch_delivery_id = delivery_id
        return backorder_ids
