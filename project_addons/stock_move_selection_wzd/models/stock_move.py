# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'


    dunmy_picking_id = fields.Many2one('stock.picking', 'Transfer Reference', store=False)

    def get_moves_selection_domain(self):
        wh_ids = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        lot_stock = wh_ids.mapped('lot_stock_id')
        domain = [
                    ('state', 'not in', ['draft', 'cancel', 'done']),
                    '|', '|', ('location_id', 'child_of', lot_stock.ids), ('location_dest_id', 'child_of', lot_stock.ids), ('location_dest_id.usage', '=', 'customer')]
        return domain

    @api.multi
    def _return_action_show_moves(self):
        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)

        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]
        action['domain'] = self.get_moves_selection_domain()

        action['views'] = [(tree and tree.id or False, 'tree'),
                           (kanban and kanban.id or False, 'kanban')]
        return action

    def get_domain_moves_to_asign(self):
        return self.filtered(lambda x: not x.picking_id and x.state not in ('done', 'cancel', 'draft'))


    @api.multi
    def move_sel_assign_picking(self):
        print (self._context)
        for move in self.get_domain_moves_to_asign():
            move.action_force_assign_picking()

    def get_domain_moves_to_deasign(self):
        return self.filtered(lambda x: x.picking_id and x.state not in ('done', 'cancel', 'draft'))

    @api.multi
    def move_de_sel_assign_picking(self):
        print(self._context)
        self.picking_id = False
        self.move_line_ids.write({'picking_id':False})


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'