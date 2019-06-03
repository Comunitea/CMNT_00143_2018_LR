# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.shipping_type.models.res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
SEARCH_F = ['urgent', 'delivery_route_path_id', 'shipping_type']

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
    count_move_draft = fields.Integer(compute='_compute_picking_count')
    count_move_done = fields.Integer(compute='_compute_picking_count')
    count_move_todo_today = fields.Integer(compute='_compute_picking_count')
    count_move_ready = fields.Integer(compute='_compute_picking_count')
    count_move = fields.Integer(compute='_compute_picking_count')
    count_move_waiting = fields.Integer(compute='_compute_picking_count')
    count_move_late = fields.Integer(compute='_compute_picking_count')
    count_move_backorders = fields.Integer(compute='_compute_picking_count')
    count_move_to_pick = fields.Integer(compute='_compute_picking_count')
    rate_move_late = fields.Integer(compute='_compute_picking_count', string="Ratio")
    rate_move_backorders = fields.Integer(compute='_compute_picking_count')
    rate_done = fields.Integer(compute='_compute_picking_count', string="Ratio")
    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE, store=False)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path", store=False)
    urgent = fields.Selection([('urgent', 'Urgente'), ('no_urgent', 'No uergente')], help='Default urgent for partner orders\nPlus 3.20%', store=False)
    context_domain = fields.Char()

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



    def _compute_move_count(self):
        # TDE TODO count picking can be done using previous two
        domains = self.get_moves_domain()
        for field in domains:
            domain = domains[field] + [('picking_type_id', 'in', self.ids)]
            data = self.env['stock.move'].read_group(domain, ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }

            for record in self:
                record[field] = count.get(record.id, 0)
        for record in self:
            count_move_today = record.count_move_todo_today + record.count_move_done
            record.rate_done = count_move_today and record.count_move_done * 100 / count_move_today or 0
            record.rate_move_late = record.count_move and record.count_move_late * 100 / record.count_move or 0
            record.rate_move_backorders = record.count_move and record.count_move_backorders * 100 / record.count_move or 0



    def _compute_picking_count(self):
        # TDE TODO count picking can be done using previous two
        ### SOBREESCRIBO LA FUNCION COMPLETA PARA AÑADIR EL SGA_STATE

        context_domain = self.get_context_domain(date_expected='scheduled_date')

        move_domains, picking_domains = self.get_moves_domain()
        for field in move_domains:
            domain = move_domains[field] + [('picking_type_id', 'in', self.ids)]
            data = self.env['stock.move'].read_group(domain, ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }

            for record in self:
                record[field] = count.get(record.id, 0)

        for field in picking_domains:
            data = self.env['stock.picking'].read_group(picking_domains[field] +
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

            count_move_today = record.count_move_todo_today + record.count_move_done
            record.rate_done = count_move_today and record.count_move_done * 100 / count_move_today or 0
            record.rate_move_late = record.count_move and record.count_move_late * 100 / record.count_move or 0
            record.rate_move_backorders = record.count_move and record.count_move_backorders * 100 / record.count_move or 0


    def get_type_domain(self, type=''):
        if type=='moves':
        ## domain para movimientos de salida listos
            type_domain = [('picking_type_id.group_code', '=', 'outgoing'), ('state', 'in', ('partially_available', 'assigned')), ('result_package_id', '!=', False)]
        else:
            type_domain=[]

        return type_domain

    def get_moves_domain(self):
        type_domain = self.get_type_domain('moves')
        c_dom = self.get_context_domain()
        context_domain = expression.AND([type_domain, c_dom])

        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        today_filter = [('date_expected', '<', tomorrow), ('date_expected', '>', today)]
        hide_state = [('state', 'not in', ('draft', 'done', 'cancel'))]
        to_do_state = [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))]
        ready_state = [('state', 'in', ('partially_available', 'assigned')), ('sga_state', 'in', ('NI', 'NE'))]

        move_domains = {
            'count_move_todo_today': context_domain + to_do_state + [('date_expected', '<', today)],
            'count_move_done': context_domain + [('state', '=', 'done'), ('date', '>', yesterday)],
            'count_move_draft': context_domain + [('state', '=', 'draft')],
            'count_move_waiting': context_domain + to_do_state,
            'count_move_ready': context_domain + ready_state + [('picking_id', '!=', False), ('date_expected', '<', tomorrow)],
            'count_move': context_domain + [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))],
            'count_move_to_pick': context_domain + ready_state + [('picking_id', '=', False), ('date_expected', '<', tomorrow)] ,
            'count_move_late': context_domain + to_do_state + [('date_expected', '<', yesterday)],
            'count_move_backorders': context_domain + to_do_state + [('origin_returned_move_id', '!=', False)],
        }
        type_domain = self.get_type_domain('picks')
        c_dom = self.get_context_domain('scheduled_date')
        context_domain = expression.AND([type_domain, c_dom])
        picking_domains = {
            'count_picking_draft': context_domain + [('state', '=', 'draft')],
            'count_picking_waiting': context_domain + [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': context_domain + [('state', '=', 'assigned'), ('sga_state', 'in', ('NI', 'NE'))],
            'count_picking': context_domain + [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': context_domain + [
                ('scheduled_date', '<', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': context_domain + [('backorder_id', '!=', False),
                                                          ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }


        return move_domains, picking_domains

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Include commercial name in direct name search."""

        args = expression.normalize_domain(args)

        for token in args:
            if isinstance(token, (list, tuple)) and token[0] in SEARCH_F:
                self = self.env['stock.picking.type'].search([]).filtered(lambda x:x.count_move)
                args = [('id', 'in', self.ids)]
                break
        return super(PickingType, self).search(
            args, offset=offset, limit=limit, order=order, count=count,
        )



    def get_context_domain(self, date_expected ='date_expected'):
        def delete(domain, var, new_token):
            print('Token: {}'.format(new_token))
            if domain:
                ##EPETIDO
                for token in domain:
                    ## Si ya lo tengo devulevo el mismo domainio
                    if token == new_token[0]:
                        print ('Token repetido: {}'.format(new_token))
                        return domain
                ##HAGO UN OR CON ALGUNO QUE YA HAY
                for token in domain:
                    ## SOlo cojo las tuplas del dominio
                    if isinstance(token, (list, tuple)):
                        field = token[0]
                        if field == var:
                            old_token = token
                            domain.remove(token)
                            domain += ['|', old_token, new_token[0]]
                            print('Token OR: {}'.format(domain))
                            return domain

            ##NO LO ENCUENTRO ES UN AND

            domain += new_token
            print('Token AND: {}'.format(domain))
            return domain

        print ('COntexto: {}'.format(self._context))
        if self._context.get('search1_all', False):
            self.write({'context_domain': '[]'})
            return []


        domain = safe_eval(self[0].context_domain or '[]', {})
        domain1 = domain
        ##Por sencillez
        try:
            var = (1, '=', 1)
            domain.remove(var)
        except:
            pass
        clear=True
        for f in SEARCH_F:
            if self._context.get('f_{}'.format(f), False):
                clear=False


        shipping_type = self._context.get('search1_shipping_type', False)
        if shipping_type:
            clear=False
            delete(domain, 'shipping_type', [('shipping_type', '=', shipping_type)])

        delivery_route_path_id = self._context.get('search1_delivery_route_path_id', False)
        if delivery_route_path_id:
            clear = False
            delete(domain, 'delivery_route_path_id', [('delivery_route_path_id', '=', delivery_route_path_id)])

        urgent = self._context.get('search1_urgent', False)
        if urgent:
            clear = False
            delete(domain, 'urgent', [('urgent', '=', urgent == 'urgent')])


        if clear:
            domain=[]

        if self._context.get('filter_day', False):

            f_day = self._context['filter_day']
            today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            yesterday = (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            if f_day =='today':
                domain = [(date_expected, '<', tomorrow),(date_expected, '>', yesterday)]
            elif f_day=='tomorrow':
                domain = [(date_expected, '>=', tomorrow)]
            elif f_day=='yesterday':
                domain = [(date_expected, '<=', today)]
        return domain or []


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
        domain = self.get_context_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_done': 1}

        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_all_not_done(self):
        domain = self.get_context_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_not_done': 1}

        return self.return_action_show_moves(domain, context)

    def get_action_picking_tree_ready(self):

        action = self.env.ref('stock.action_picking_tree_ready').read()[0]
        action['domain'] = self.get_context_domain()
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
        domain = self.get_context_domain() + [('state', '!=', 'draft')]
        context = {
            'search_default_picking_type_id': self.id,
            }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_no_pick(self):
        domain = self.get_context_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_without_pick': 1
            }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_no_package(self):
        domain = self.get_context_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_with_no_package': 1
            }
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_pasaran(self):
        domain = self.get_context_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_todo': 1,
            'search_default_without_pick': 1,
            'search_default_pasaran_route': 1
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_todo_today(self):
        domain = self.get_context_domain() +  [
                  ('date_expected', '<', (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)),
                  ('date_expected', '>', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))]
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_ready': 1,
        }
        return self.return_action_show_moves(domain, context)


