# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


PICKING_TYPE_GROUP = [('incoming', 'Incoming'),
                      ('outgoing', 'Outgoing'),
                      ('picking', 'Picking'),
                      ('internal', 'Internal'),
                      ('location','Location'),
                      ('reposition','Reposition'),
                      ('other','Other')]

SGA_STATES = [('NI', 'Sin integracion'),
              ('NE', 'No enviado'),
              ('PS', 'Pendiente Sga'),
              ('EE', 'Error en exportacion'),
              ('EI', 'Error en importacion'),
              ('SR', 'Realizado'),
              ('SC', 'Cancelado')]


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    group_code = fields.Selection(PICKING_TYPE_GROUP, string="Code group")

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
    count_move_to_pick = fields.Integer(compute='_compute_move_count')
    rate_move_late = fields.Integer(compute='_compute_move_count', string="Ratio")
    rate_move_backorders = fields.Integer(compute='_compute_move_count')
    rate_done = fields.Integer(compute='_compute_move_count', string="Ratio")
    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')


    def get_sga_integrated(self):
        return self.sga_integrated

    def get_parent_state(self, child_ids):
        ### LO PONGO AQUI PORQUE ES DONDE ESTA SGA_STATE
        if all(child.sga_state == 'NI' for child in child_ids):
            sga_state = 'NI'
        elif all(child.sga_state == 'SR' for child in child_ids):
            sga_state = 'SR'
        elif all(child.sga_state == 'PS' for child in child_ids):
            sga_state = 'PS'
        elif all(child.sga_state == 'SC' for child in child_ids):
            sga_state = 'SC'
        elif all(child.sga_state == 'NE' for child in child_ids):
            sga_state = 'NE'
        elif all(child.sga_state in ('SR', 'PS') for child in child_ids):
            sga_state = 'PS'
        elif any(child.sga_state == 'EI' for child in child_ids):
            sga_state = 'EI'
        elif any(child.sga_state == 'EE' for child in child_ids):
            sga_state = 'EE'
        else:
            sga_state = 'EE'
        return sga_state

    def get_moves_domain(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        today_filter = [('date_expected', '<', tomorrow), ('date_expected', '>', today)]
        hide_state = [('state', 'not in', ('draft', 'done', 'cancel'))]
        to_do_state = [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))]
        ready_state = [('state', 'in', ('partially_available', 'assigned')), ('sga_state', 'in', ('NI', 'NE'))]

        domains = {
            'count_move_todo_today': to_do_state + [('date_expected', '<', today)],
            'count_move_done': [('state', '=', 'done'), ('date', '>', yesterday)],
            'count_move_draft': [('state', '=', 'draft')],
            'count_move_waiting': to_do_state,
            'count_move_ready': ready_state + [('picking_id', '!=', False), ('date_expected', '<', tomorrow)],
            'count_move': [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))],
            'count_move_to_pick': ready_state + [('picking_id', '=', False), ('date_expected', '<', tomorrow)] ,
            'count_move_late': to_do_state + [('date_expected', '<', yesterday)],
            'count_move_backorders': to_do_state + [('origin_returned_move_id', '!=', False)],
        }
        return domains

    def _compute_move_count(self):
        # TDE TODO count picking can be done using previous two
        domains = self.get_moves_domain()

        for field in domains:
            data = self.env['stock.move'].read_group(domains[field] +
                [('picking_type_id', 'in', self.ids)],
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

    def update_context(self, context={}):

        if self.group_code == 'picking':
            context.update({
                'search_default_by_shipping_type': True,
                'search_default_by_delivery_path_route_id': True,
                'search_default_by_carrier_id': True

            })

        elif self.group_code=='outgoing':
            context.update({
                'search_default_by_shipping_type':True,
                'search_default_by_delivery_route_path_id':True,
                'search_default_by_carrier_id': True,
                'search_default_by_partner_id':True
            })
        elif self.group_code=='incoming':
            context.update({
                'search_default_partner_id':1,

            })
        elif self.group_code == 'location':
            context.update({
                'search_default_location_dest_id': 1,
            })

        elif self.group_code == 'internal':
            context.update({
                'search_default_location_id': 1,
                'search_default_location_dest_id': 1,
            })



        return context




    @api.multi
    def return_action_show_moves(self, domain=[], context={}, group_code=''):

        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]

        action['domain'] = domain
        action['views'] = [(tree and tree.id or False, 'tree'), (False, 'form'),
                           (kanban and kanban.id or False, 'kanban')]

        self.update_context(context)
        if context:
            action['context'] = context

        name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        if name_str:
            action['display_name'] = "---------> {} Moves".format(name_str[0])

        print (action['context'])
        return action


    def get_action_move_tree_late(self):
        domain = self.get_moves_domain()['count_move_late']
        context = {
                   'search_default_picking_type_id': self.id,
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_backorder(self):
        domain = self.get_moves_domain()['count_move_backorders']
        context = {
                   'search_default_picking_type_id': self.id,}
        return self.return_action_show_moves(domain, context)

    def get_action_move_to_picking_ready(self):
        domain = self.get_moves_domain()['count_move_to_pick']
        context = {
                   'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)

    def get_action_move_to_sga_ready(self):
        domain = self.get_moves_domain()['count_move_ready']
        context = {
                   'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_waiting(self):
        domain = self.get_moves_domain()['count_move_waiting']
        context = {
            'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_ready(self):
        domain = self.get_moves_domain()['count_move_ready']
        context = {
            'search_default_picking_type_id': self.id,}

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

    def get_action_picking_tree_ready(self):

        action = self.env.ref('stock.action_picking_tree_ready').read()[0]
        if self.sga_integrated:
            action['context'] ={'search_default_picking_type_id': [self.id],
                                'default_picking_type_id': self.id,
                                'contact_display': 'partner_address',
                                'search_default_available': 1,
                                'hide_sga_state': False}
        if self:
            action['display_name'] = self.display_name
        return action

    def get_stock_move_action_move_type_today(self):

        domain = self.get_moves_domain()['count_move_todo_today']
        context = {
            'search_default_picking_type_id': self.id,
        }
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

    def get_action_move_tree_no_package(self):
        domain = []
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_with_no_package': 1
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


    def _compute_picking_count(self):
        # TDE TODO count picking can be done using previous two
        ### SOBREESCRIBO LA FUNCION COMPLETA PARA AÑADIR EL SGA_STATE

        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', '=', 'assigned'), ('sga_state', 'in', ('NI', 'NE'))],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('scheduled_date', '<', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }
        for field in domains:
            data = self.env['stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)
        for record in self:
            record.rate_picking_late = record.count_picking and record.count_picking_late * 100 / record.count_picking or 0
            record.rate_picking_backorders = record.count_picking and record.count_picking_backorders * 100 / record.count_picking or 0

