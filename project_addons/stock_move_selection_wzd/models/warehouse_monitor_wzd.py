# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class WarehouseMonitorWzd(models.Model):

    _name = "warehouse.monitor.report"
    _description = 'Warehouse monitor'
    _inherits = {'stock.picking.type': 'type_id'}



    @api.multi
    def get_report_field(self):
        pick_state = ['waiting', 'confirmed', 'assigned']
        move_state = ['waiting', 'confirmed', 'assigned', 'partially_available']
        for type in self:

            moves_domain = [('picking_type_id', '=', type.id), ('picking_id', '=', False), ('state', 'in', move_state)]
            picking_domain = [('picking_type_id', '=', type.id), ('state', 'in', pick_state)]

            todo_picking_ids = self.env['stock.picking'].search(picking_domain)
            c_todo_picking_ids = len(todo_picking_ids)

            move_line = self.env['stock.picking'].search(moves_domain)
            todo_move_line = todo_picking_ids.mapped('move_line')
                            # '|', '&', ('state', 'not in', ['draft', 'cancel']), ('date_expected', '<=', fields.datetime.now() + timedelta(days=1)),
                            # '&', ('state', '=' , 'done'),  ('date', '>=', fields.datetime.now() - timedelta(days=1))
                            # ]
            todo_move_line = move_line.filtered(lambda x:x.state != 'done')


    type_id = fields.Many2one('stock.picking.type')
    move_line = fields.One2many('stock.move')
    move_line_ids = fields.One2many('stock.move.line')
    #picking_ids = fields.One2many('stock.picking')
    todo_picking_ids = fields.One2many('stock.picking')
    c_todo_picking_ids = fields.Integer('Pickings to do')
    todo_move_line = fields.One2many('stock.move')
    c_todo_move_line = fields.Integer('Moves to do')
    todo_move_line_ids = fields.One2many('stock.move.line')
    c_todo_move_line_ids = fields.Integer('Moves to do')