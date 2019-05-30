# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import SGA_STATES


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")

    def action_view_moves_line(self):

        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]

        action['domain'] = [('id', 'in', self.move_line_ids.mapped('move_id').ids)]
        action['views'] = [(tree and tree.id or False, 'tree'), (False, 'form'),
                           (kanban and kanban.id or False, 'kanban')]
        action['context'] = {}
        return action