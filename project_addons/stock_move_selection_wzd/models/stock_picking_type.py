# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from collections import namedtuple
import json

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from .stock_picking import PICKING_TYPE_GROUP

class PickingType(models.Model):
    _inherit = "stock.picking.type"


    # Statistics for the kanban view for moves
    last_done_move = fields.Char('Last 10 Done Pickings', compute='_compute_last_done_moves')
    count_move_draft = fields.Integer(compute='_compute_move_count')
    count_move_done = fields.Integer(compute='_compute_move_count')
    count_move_todo_today = fields.Integer(compute='_compute_move_count')
    count_move_ready = fields.Integer(compute='_compute_move_count')
    count_move = fields.Integer(compute='_compute_move_count')
    count_move_waiting = fields.Integer(compute='_compute_move_count')
    count_move_late = fields.Integer(compute='_compute_move_count')
    count_move_backorders = fields.Integer(compute='_compute_move_count')

    rate_move_late = fields.Integer(compute='_compute_move_count', string="Ratio")
    rate_move_backorders = fields.Integer(compute='_compute_move_count')
    rate_done = fields.Integer(compute='_compute_move_count', string="Ratio")

    def _compute_move_count(self):
        # TDE TODO count picking can be done using previous two

        domains = {
            'count_move_todo_today': [('state', 'not in', ('done', 'draft', 'cancel')),
                                    ('date_expected', '<', (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                    ('date_expected', '>', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))],
            'count_move_done': [('state', '=', 'done'), ('date', '>', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))],
            'count_move_draft': [('state', '=', 'draft')],
            #'count_move_today_todo': [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed')), ('date_expected', '=', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))],
            'count_move_waiting': [('state', 'in', ('partially_available', 'confirmed', 'waiting'))],
            'count_move_ready': [('state', 'in', ('partially_available','assigned'))],
            'count_move': [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))],
            'count_move_late': [('date_expected', '<', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))],
            'count_move_backorders': [('origin_returned_move_id', '!=', False), ('state', 'in', ('partially_available', 'confirmed', 'assigned', 'waiting'))],
        }
        for field in domains:
            data = self.env['stock.move'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            print (data)
            for record in self:
                record[field] = count.get(record.id, 0)
        for record in self:
            count_move_today = record.count_move_todo_today + record.count_move_done
            record.rate_done = count_move_today and record.count_move_done * 100 / count_move_today or 0
            record.rate_move_late = record.count_move and record.count_move_late * 100 / record.count_move or 0
            record.rate_move_backorders = record.count_move and record.count_move_backorders * 100 / record.count_move or 0


    @api.one
    def _compute_last_done_moves(self):
        # TDE TODO: true multi
        tristates = []
        for move in self.env['stock.move'].search([('picking_type_id', '=', self.id), ('state', '=', 'done')], order='date_done desc', limit=20):
            if move.date_done > move.date:
                tristates.insert(0, {'tooltip': move.name or '' + ": " + _('Late'), 'value': -1})
            else:
                tristates.insert(0, {'tooltip': move.name or '' + ": " + _('OK'), 'value': 1})
        self.last_done_move = json.dumps(tristates)



    @api.multi
    def return_action_show_moves(self, domain=[], context={}, group_code=''):

        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]

        action['domain'] = domain
        action['views'] = [(tree and tree.id or False, 'tree'), (False, 'form'),
                           (kanban and kanban.id or False, 'kanban')]

        if context:
            action['context'] = context

        name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        if name_str:
            action['display_name'] = "---------> {} Moves".format(name_str[0])

        print (action['context'])
        return action


    def get_action_move_tree_late(self):
        domain = []
        context = {
                   'search_default_picking_type_id': self.id,
                   'search_default_late': 1,
                   'search_default_todo': 1
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_backorder(self):
        domain = []
        context = {
                   'search_default_picking_type_id': self.id,
                   'search_default_returns': 1,
                   'search_default_todo': 1}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_waiting(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_ready(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_ready': 1}

        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_all_done(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_done': 1}

        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_all_not_done(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_not_done': 1}

        return self.return_action_show_moves(domain, context)


    def get_stock_move_action_move_type(self):
        domain = [('state', '!=', 'draft')]
        context = {
            'search_default_picking_type_id': self.id,
            }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_no_pick(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_without_pick': 1
            }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_pasaran(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_without_pick': 1,
            'search_default_pasaran_route': 1
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_todo_today(self):
        domain = [
                  ('date_expected', '<', (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)),
                  ('date_expected', '>', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))]
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_ready': 1,
        }
        return self.return_action_show_moves(domain, context)
