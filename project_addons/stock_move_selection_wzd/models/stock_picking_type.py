# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


SEARCH_F = ['urgent', 'delivery_route_path_id', 'shipping_type']

PICKING_TYPE_GROUP = [('incoming', 'Incoming'),
                      ('outgoing', 'Outgoing'),
                      ('picking', 'Picking'),
                      ('internal', 'Internal'),
                      ('location', 'Location'),
                      ('reposition', 'Reposition'),
                      ('other', 'Other')]


SGA_STATES = [('no_integrated', 'Sin integracion'),
              ('no_send', 'No enviado'),
              ('ready', 'Para enviar'),
              ('pending', 'Pendiente Sga'),
              ('export_error', 'Error en exportacion'),
              ('import_error', 'Error en importacion'),
              ('done', 'Realizado'),
              ('cancel', 'Cancelado')]

SGA_INTEGRATION_TYPES = [('sga_ulma', 'SGA ULMA'),
                         ('sga_adaia', 'SGA ADAIA')]


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_unpacked = fields.Boolean('Movimientos sin paquete', help='En ordenes de carga, si no está marcado genera automaticamente un paquete para el movimiento')
    allow_unbatched = fields.Boolean('Albaranes sin grupo', help='En ordenes de carga, si no está marcado genera automaticamente un grupo para el albarán')

    group_code = fields.Selection(PICKING_TYPE_GROUP, string="Code group")
    visible_kanban_conf = fields.Boolean('Configuración de Kanban', default="1")
    # Statistics for the kanban view for moves

    count_move_draft = fields.Integer(compute='_compute_picking_count', string="Movs. borrador")

    visible_last_done_move= fields.Boolean('Ultimos movs')
    last_done_move = fields.Char('Ultimos movs', compute='_compute_last_done_moves')


    count_move_done = fields.Integer(compute='_compute_picking_count', string="Movs. realizados")
    visible_count_move_done = fields.Boolean('Movs. realizados')

    count_move_todo_today = fields.Integer(compute='_compute_picking_count', string="Movs para realizar hoy")
    visible_count_move_todo_today = fields.Boolean('Movs para realizar hoy')

    count_move_ready = fields.Integer(compute='_compute_picking_count', string="Movs. preparados para validar")
    visible_count_move_ready = fields.Boolean('Movs. preparados para validar')

    count_move_waiting = fields.Integer(compute='_compute_picking_count', string="Movs. esperando disponibilidad u otra operación")
    visible_count_move_waiting = fields.Boolean('Movs. esperando disponibilidad u otra operación')

    count_move_late = fields.Integer(compute='_compute_picking_count', string="Movs. retrasados")
    visible_count_move_late = fields.Boolean('Movs. retrasados')

    count_move_backorders = fields.Integer(compute='_compute_picking_count', string="Movs. de 2º albarán")
    visible_count_move_backorders = fields.Boolean('Movs. de 2º albarán')

    visible_count_move_to_pick = fields.Boolean('Movs. sin batch')
    count_move_to_pick = fields.Integer(compute='_compute_picking_count', string="Movs. sin grupo")

    visible_count_pick_to_batch = fields.Boolean('Reservas sin carga')
    count_pick_to_batch = fields.Integer(compute='_compute_picking_count', string="Reservas sin carga")

    visible_count_batch_ready = fields.Boolean('Albaranes/Grupos preparados para enviar/validar')
    count_batch_ready = fields.Integer(compute='_compute_picking_count', string="Albaranes/Grupos preparados para enviar/validar")

    visible_count_move_unpacked= fields.Boolean('Movs. sin empaquetar')
    count_move_unpacked = fields.Integer(compute='_compute_picking_count', string="Movs. sin empaquetar")

    count_sga_send = fields.Integer(compute='_compute_picking_count', string="Movs. enviados a SGA")
    count_sga_done = fields.Integer(compute='_compute_picking_count', string="Movs. hechos en SGA")
    count_sga_error = fields.Integer(compute='_compute_picking_count', string="Errores de SGA")

    visible_bargraph = fields.Boolean('Barras inferiores')
    visible_ratio = fields.Boolean('Ratio')

    visible_count_picking_waiting = fields.Boolean('Albaranes en espera')
    visible_count_picking_ready = fields.Boolean('Albaranes preparados')
    visible_count_picking = fields.Boolean('Albaranes')
    visible_count_picking_late = fields.Boolean('Albaranes tarde')
    visible_count_picking_backorders = fields.Boolean('2º albarán')



    count_move = fields.Integer(compute='_compute_picking_count', string='Movs. totales')
    rate_move_late = fields.Integer(compute='_compute_picking_count', string="Ratio")
    rate_move_backorders = fields.Integer(compute='_compute_picking_count')
    rate_done = fields.Integer(compute='_compute_picking_count', string="Ratio")
    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_integration_type = fields.Selection(SGA_INTEGRATION_TYPES, string="SGA Integration type")

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE, store=False)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path", store=False)
    urgent = fields.Selection([('urgent', 'Urgente'), ('no_urgent', 'No uergente')], help='Default urgent for partner orders\nPlus 3.20%', store=False)
    context_domain = fields.Char()

    partner_id = fields.Many2one('res.partner', 'Cliente/Proveedor', store=False)


    def get_sga_integrated(self):
        return self.sga_integrated

    def get_parent_state(self, child_ids):
        ### LO PONGO AQUI PORQUE ES DONDE ESTA SGA_STATE
        if all(child.sga_state == 'no_integrated' for child in child_ids):
            sga_state = 'no_integrated'
        elif all(child.sga_state == 'done' for child in child_ids):
            sga_state = 'done'
        elif all(child.sga_state == 'pending' for child in child_ids):
            sga_state = 'pending'
        elif all(child.sga_state == 'cancel' for child in child_ids):
            sga_state = 'cancel'
        elif all(child.sga_state == 'no_send' for child in child_ids):
            sga_state = 'no_send'
        elif all(child.sga_state in ('done', 'pending') for child in child_ids):
            sga_state = 'pending'
        elif any(child.sga_state == 'import_error' for child in child_ids):
            sga_state = 'import_error'
        elif any(child.sga_state == 'export_error' for child in child_ids):
            sga_state = 'export_error'
        else:
            sga_state = 'export_error'
        return sga_state

    def _compute_picking_count(self):
        # TDE TODO count picking can be done using previous two
        ### SOBREESCRIBO LA FUNCION COMPLETA PARA AÑADIR EL SGA_STATE
        context_domain = self.get_context_domain(date_expected='scheduled_date')
        move_domains, picking_domains, batch_domains = self.get_moves_domain()

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
        for field in batch_domains:
            data = self.env['stock.batch.picking'].read_group(batch_domains[field] +
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


    def get_ready_state(self):

        ## todo: MEJORAR ESTO
        ready_domain = {}

        #internal moves
        int_dom = ['&', '&', ('picking_type_id.code', '=', 'internal'),
                   ('sga_state', 'in', ('no_send', 'no_integrated')),
                   ('state', 'in', ('partially_available', 'assigned'))]
        #recepciones
        ready_dom = [('state', 'in', ('partially_available', 'assigned')) , '|', '|',
                   ('picking_type_id.code', '=', 'incoming'),
                  '&', ('picking_type_id.code', '=', 'internal'), ('sga_state', 'in', ('no_send', 'no_integrated')),
                  '&', ('picking_type_id.code', '=', 'outgoing'), ('result_package_id', '!=', False)]
        #salidas
        out_dom = ['&', '&', ('picking_type_id.code', '=', 'outgoing'),
                   ('state', 'in', ('partially_available', 'assigned')),
                   ('result_package_id', '!=', False)]

        ready_domain['move'] = ready_dom
        #ready_domain['move'] = [('state', 'in', ('partially_available', 'assigned'))]
        int_dom = [('picking_type_id.code', '=', 'internal'), ('state', '=', 'assigned')]
        # recepciones
        in_dom = [('picking_type_id.code', '=', 'incoming'), ('state', '=', 'assigned')]
        # salidas
        out_dom = [('picking_type_id.code', '=', 'outgoing'),
                   ('batch_picking_id', '!=', False), ('state', '=', 'assigned')]
        #ready_domain['move'] = [('state', 'in', ('partially_available', 'assigned'))]
        ready_domain['pick'] = [('state', 'in', ('partially_available', 'assigned'))]
        ready_domain['batch'] = [('state', 'in', ('draft', 'assigned'))]

        return ready_domain

    def get_moves_domain(self):
        c_dom = []
        context_domain = self.get_context_domain()
        if c_dom:
            context_domain = expression.AND([c_dom, context_domain])

        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        draft = [('state', '=', 'draft')]
        done = [('state', '=', 'done')]
        today_filter = [('date_expected', '<', tomorrow), ('date_expected', '>', today)]
        hide_state = [('state', 'not in', ('draft', 'done', 'cancel'))]
        context_domain += hide_state
        to_do_state = [('state', 'in', ('partially_available', 'assigned', 'waiting', 'confirmed'))]

        waiting_state = [('state', 'in', ('waiting','partially_available', 'confirmed'))]
        no_stock_state = [('state', 'in', ('partially_available', 'confirmed'))]
        ready_state = self.get_ready_state()

        with_pick = ['|', ('draft_batch_picking_id', '!=', False), ('batch_picking_id', '!=', False)]
        without_pick = [('draft_batch_picking_id', '=', False), ('batch_picking_id', '=', False)]

        with_batch = [('batch_delivery_id', '!=', False)]
        without_batch = [('batch_delivery_id', '=', False)]

        with_result_package = [('result_package_id', '!=',False )]
        without_result_package = [('result_package_id', '=', False)]
        before_tomorrow = [('date_expected', '<', tomorrow)]
        late = [('date_expected', '<', yesterday)]
        move_domains = {
            'count_move_todo_today': context_domain + to_do_state + before_tomorrow,
            'count_move_done': context_domain + done + [('date', '>', yesterday)],
            'count_move_draft': context_domain + draft,
            'count_move_waiting': context_domain + waiting_state,
            'count_move_unpacked': context_domain + [('result_package_id', '=', False), ('state', 'in', ('partially_available', 'assigned'))],
            'count_move_ready': context_domain + ready_state['move'],
            'count_move': context_domain + to_do_state,
            'count_move_to_pick': context_domain  + without_pick + ready_state['move'],
            'count_move_late': context_domain + to_do_state + late,
            'count_move_backorders': context_domain + to_do_state + [('origin_returned_move_id', '!=', False)],
            'count_sga_send': context_domain +[('sga_state', '=', 'pending')],
            'count_sga_done': context_domain +[('sga_state', '=', 'pending'), ('quantity_done', '=', 0)],
            'count_sga_error': context_domain +[('sga_state', 'in', ('export_error', 'import_error'))]

        }
        context_domain = []#self.get_context_domain('scheduled_date')
        picking_domains = {
            'count_picking_draft': context_domain + draft,
            'count_picking_waiting': context_domain + [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': context_domain + ready_state['pick'],
            'count_picking': context_domain + to_do_state,
            'count_picking_late': context_domain +
                [('scheduled_date', '<', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT))] +
                to_do_state,
            'count_picking_backorders': context_domain + [('backorder_id', '!=', False)] + to_do_state,
            'count_pick_to_batch': context_domain + ready_state['pick']
        }
        batch_domains = {
            'count_batch_ready': context_domain + ready_state['batch'],
        }

        return move_domains, picking_domains, batch_domains

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
            if domain:
                ##EPETIDO
                for token in domain:
                    ## Si ya lo tengo devulevo el mismo domainio
                    if token == new_token[0]:
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
                            return domain

            ##NO LO ENCUENTRO ES UN AND

            domain += new_token
            return domain

        if self._context.get('search1_all', False):
            self.write({'context_domain': '[]'})
            return []


        domain = safe_eval(self[0].context_domain or '[]', {})

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
                domain += [(date_expected, '<', tomorrow),(date_expected, '>=', today)]
            elif f_day=='tomorrow':
                domain += [(date_expected, '>=', tomorrow)]
            elif f_day=='late':
                domain += [(date_expected, '<=', today)]

        if self._context.get('search_partner_id', False):
            partner_id = self.env['res.partner'].search([('display_name', 'ilike', self._context['search_partner_id'])])
            if partner_id:
                domain += [('partner_id', 'in', partner_id.ids)]
        if self._context.get('search_shipping_type', False):
            domain += [('shipping_type', '=', self._context.get('search_shipping_type', False) )]

        tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

        print('{} {}'.format("Contet domain", domain))


        return domain or []


    @api.one
    def _compute_last_done_moves(self):
        # TDE TODO: true multi
        tristates = []
        for move in self.env['stock.move'].search([('picking_type_id', '=', self.id), ('state', '=', 'done')], order='date desc', limit=20):
            if move.date > move.date_expected:
                tristates.insert(0, {'tooltip': move.name or '' + ": " + _('Late'), 'value': -1})
            else:
                tristates.insert(0, {'tooltip': move.name or '' + ": " + _('OK'), 'value': 1})
        self.last_done_move = json.dumps(tristates)

    def update_context(self, context={}):
        context.update({'group_code': self.group_code})
        if self.group_code == 'picking':
            context.update({
                'search_default_by_shipping_type': True,
                'search_default_by_delivery_route_path_id': True,
            })

        elif self.group_code == 'outgoing':
            context.update({
                'search_default_by_partner_id': True,
                'search_default_by_shipping_type': True,
            })
        elif self.group_code == 'incoming':
            context.update({
                'search_default_by_partner_id': True,
            })
        elif self.group_code == 'location':
            context.update({
                'search_default_by_location_dest_id': True,
            })
        elif self.group_code == 'internal':
            context.update({
                'search_default_by_location_id': True,
                'search_default_by_location_dest_id': True,
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

        action['name'] = self.name
        action['display_name'] = self.name
        #name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        #if name_str:
        #    action['display_name'] = "---------> {} Moves".format(name_str[0])
        return action


    def get_action_move_tree_late(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_late']
        context = {
                   'search_default_picking_type_id': self.id,
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_backorder(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_backorders']
        context = {
                   'search_default_picking_type_id': self.id,}
        return self.return_action_show_moves(domain, context)

    def get_action_move_to_picking_ready(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_to_pick']
        context = {
                   'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)

    def get_action_move_to_sga_ready(self):

        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_ready']
        context = {
                   'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_waiting(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_waiting']
        context = {
            'search_default_picking_type_id': self.id}
        return self.return_action_show_moves(domain, context)


    def get_action_move_tree_ready(self):

        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_ready']
        context = {
            'search_default_picking_type_id': self.id,}

        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_all_done(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_done': 1}

        return self.return_action_show_moves(move_domains, context)

    def get_action_move_tree_all_not_done(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        context = {
            'search_default_picking_type_id': self.id,
            'search_default_not_done': 1}

        return self.return_action_show_moves(move_domains, context)

    def get_action_picking_tree_ready(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        action = self.env.ref('stock.action_picking_tree_ready').read()[0]
        action['domain'] = self.get_context_domain('scheduled_date')
        if self.sga_integrated:
            action['context'] ={'search_default_picking_type_id': [self.id],
                                'default_picking_type_id': self.id,
                                'contact_display': 'partner_address',
                                'search_default_available': 1,
                                'hide_sga_state': False}
        if self:
            action['display_name'] = self.display_name
        return action

    def get_action_batch_picking_tree_ready(self):

        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        action = self.env.ref('stock_batch_picking.action_stock_batch_picking_tree').read()[0]
        action['domain'] = batch_domains['count_batch_ready'] + [('picking_type_id', '=', self.id)]
        if self:
            action['display_name'] = self.display_name
        return action

    def get_action_move_tree_sga_error (self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_sga_error']
        context = {
            'search_default_picking_type_id': self.id,
        }
        return self.return_action_show_moves(domain, context)

    def get_action_move_tree_send_sga (self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_sga_send']
        context = {
            'search_default_picking_type_id': self.id,
        }
        return self.return_action_show_moves(domain, context)

    def get_stock_move_action_move_type_today(self):
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_todo_today']
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
        move_domains, picking_domains, batch_domains = self.get_moves_domain()
        domain = move_domains['count_move_unpacked']
        context = {
            'search_default_picking_type_id': self.id,
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

    @api.multi
    def _return_action_show_types(self, group_code=''):

        kanban = self.env.ref('stock_move_selection_wzd.stock_picking_type_kanban_moves', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_kanban_view').read()[0]
        action['domain'] = [('group_code', '=', group_code)]
        action['views'] = [(kanban and kanban.id or False, 'kanban')]

        action['context'] = {
                             }

        name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        if name_str:
            action['display_name'] = "---------> {} Moves".format(name_str[0])
        return action
