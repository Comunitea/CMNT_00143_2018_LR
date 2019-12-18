# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .stock_picking_type import PICKING_TYPE_GROUP
from .stock_picking_type import SGA_STATES
from odoo.osv import expression

class StockMove(models.Model):
    _inherit = 'stock.move'



    @api.multi
    def get_color_status(self):
        for move in self:
            if move.state in ('draft', 'cancel'):
                move.decoration = 'muted'
            elif move.sga_state in ('export_error', 'import_error') or move.sga_state == 'done' and move.state != 'done':
                move.decoration = 'danger'
            elif move.sga_state == 'pending':
                move.decoration = 'warning'
            elif move.state == 'done':
                move.decoration = 'success'
            elif move.group_code != 'outgoing' and move.state in ('waiting', 'confirmed'):
                move.decoration = 'muted'
            elif move.group_code in ('location', 'outgoing') and move.state == 'confirmed':
                move.decoration = 'danger'
            elif move.group_code == 'picking':
                if move.quantity_done >= 0:
                    move.decoration == 'primary'
            elif move.group_code == 'outgoing':
                if move.result_package_id and move.batch_picking_id:
                    move.decoration = 'primary'
                else:
                    move.decoration = 'warning'

            else:
                move.decoration = ''

    ##NEcesito traer estos campos de stock_move_line
    package_id = fields.Many2one('stock.quant.package', 'Paquete origen',
                                 inverse='set_package_id_to_lines',
                                 compute="get_package_id_from_line",
                                 copy=False)
    result_package_id = fields.Many2one('stock.quant.package', 'Paquete destino',
                                        inverse='set_result_package_id_to_lines',
                                        compute="get_result_package_id_from_line",
                                        store=True,
                                        copy=False)
    lot_id = fields.Many2one('stock.production.lot', 'Lote')
    dunmy_picking_id = fields.Many2one('stock.picking', 'Transfer Reference', store=False)
    delivery_route_group_id = fields.Many2one('delivery.route.path.group', 'Grupo de entrega', store=False)
    sga_integrated = fields.Boolean(related="picking_type_id.sga_integrated")
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", copy=False)
    batch_delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga', copy=False, store=True)
    batch_picking_id = fields.Many2one(related='picking_id.batch_picking_id', string='Grupo', store=True)
    draft_batch_picking_id = fields.Many2one('stock.batch.picking', string='Grupo', copy=False)
    batch_id = fields.Many2one('stock.batch.picking', compute="get_effective_batch_id", inverse='set_effective_batch_id', string='Grupo')
    code = fields.Selection(related='picking_type_id.code')
    group_code = fields.Selection(related='picking_type_id.group_code')
    decoration = fields.Char(compute = get_color_status)
    ghost_qty_done = fields.Integer(string="Cant. actual hecha",
                                    store=False,
                                    help='Se usa para buscar movimientos con qty done hecha en bd')

    visible_count_move_to_pick = fields.Boolean(related='picking_type_id.visible_count_move_to_pick')
    visible_count_move_unpacked = fields.Boolean(related='picking_type_id.visible_count_move_unpacked')
    orig_picking_id = fields.Many2one(related='move_orig_ids.picking_id', string="Origen ...")

    @api.depends('state', 'picking_id')
    def _compute_is_initial_demand_editable(self):
        ctx = self._context.copy()
        ctx.update(planned_picking=True)
        return super(StockMove, self.with_context(ctx))._compute_is_initial_demand_editable()

    @api.model
    def create(self, vals):
        return super().create(vals)

    def check_allow_change_route_fields(self):
        super().check_allow_change_route_fields()
        if any(move.batch_id for move in self.move_line_ids) and not self._context.get('force_route_vals', False):
            raise ValidationError (_('No puedes cambiar en movimientos en un batch'))
        return True

    @api.multi
    @api.depends('state', 'draft_batch_picking_id', 'batch_picking_id')
    def get_effective_batch_id(self):

        for move in self:
            move.batch_id = move.batch_picking_id if move.state == 'done' else move.draft_batch_picking_id

    @api.multi
    def set_effective_batch_id(self):
        self.filtered(lambda x: x.state not in ('done', 'cancel')).write({'draft_batch_picking_id': self.batch_id})

    @api.multi
    def unpack(self):
        for move in self:
            if move.state != 'done':
                move.write({'result_package_id': False})
        move.move_line_ids.unpack()
        return True

    @api.multi
    def action_set_envio_sga(self):
        for move in self.filtered(lambda x: x.sga_state in ('no_send', 'ready') and x.state not in ('cancel', 'done')):
            if move.sga_state=='no_send':
                if move.state == 'waiting':
                    raise ValidationError ('No puedes enviar nada a SGA sin disponibilidad.')
                move.sga_state = 'ready'
            elif move.sga_state == 'ready':
                move.sga_state = 'no_send'

    def _assign_package(self, package):
        if self.result_package_id:
            if self.result_package_id.batch_delivery_id:
                raise ValidationError ('No puedes cambiar un paquete de una orden de carga. Primero deberás quitarlo de la orden de carga')
        if self.state == 'done':
            raise ValidationError(
                'No puedes cambiar un paquete en un movimiento ya realizado')
        self.result_package_id = package
        #if package:
        #    vals = package.update_info_route_vals()
        #    if package.batch_delivery_id:
        #        vals.update(batch_delivery_id=package.batch_delivery_id.id)
        #    self.write(vals)

    @api.multi
    def assign_package(self, package):
        for move in self:
            move._assign_package(package)

    def get_new_location_vals(self, location_field, location):
        vals = super().get_new_location_vals(location_field, location)
        if location.picking_type_id and vals:
            vals.update(sga_integrated=location.picking_type_id.sga_integrated,
                        sga_state='no_send' if location.picking_type_id.sga_integrated else 'no_integrated')
        return vals

    def get_new_vals(self):
        vals = super().get_new_vals()
        vals.update(sga_integrated=self.picking_type_id and self.picking_type_id.sga_integrated,
                    sga_state='no_send' if self.picking_type_id.sga_integrated else 'no_integrated')
        return vals

    def get_moves_selection_domain(self, group_code=''):
        wh_ids = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        lot_stock = wh_ids.mapped('lot_stock_id')
        domain = []
        if group_code:
            domain += [('picking_type_id.group_code', '=', group_code)]
        domain += [('state', 'not in', ['draft', 'cancel', 'done'])]
        return domain

    def get_affected_moves(self):
        ## Cuando selecciono un movimiento o varios debo seleccionar todos los que van en el mismo paquete

        result_package_ids = self.filtered(lambda x: x.state not in ('draft', 'cancel')).mapped("move_line_ids").mapped('result_package_id')
        if result_package_ids:
            return result_package_ids.mapped("move_line_ids").mapped('move_id')
        else:
            return self

    def action_add_moves_to_batch_picking(self):
        moves_ids = self.get_affected_moves()
        ## Cuando selecciono un movimiento o varios debo seleccionar todos los que van en el mismo paquete
        ctx = self._context.copy()
        if 'active_domain' in ctx.keys():
            ctx.pop('active_domain')
        obj = self.env['stock.batch.picking.wzd']
        wzd_id = obj.create_from('stock.move', moves_ids.ids)
        action = wzd_id.get_formview_action()
        action['target'] = 'new'
        #return action

        action = self.env.ref('stock_move_selection_wzd.open_view_create_batch_picking').read()[0]
        action['res_id'] = wzd_id.id

        return action

    @api.multi
    def action_remove_moves_to_batch_picking(self):
        for move in self:
            if move.batch_delivery_id:
                raise ValidationError (_('No puedes quitar de un albarán un movimiento que está en una orden de carga. Primero quita el albarán de la orden de carga'))
            if move.result_package_id:
                raise ValidationError (_('No puedes quitar de un albarán un movimiento empaquetado, desempaquetalo primero'))
            move.draft_batch_picking_id = False
            move.picking_id = False
            move._assign_picking()


    @api.multi
    def assign_batch_picking_id(self, batch_picking_id):
        if not batch_picking_id or batch_picking_id.state != 'draft':
            raise ValidationError (_('No encuenttro un grupo disponible o está en estado incorrecto'))

        picking_ids = self.mapped('picking_id')
        #Escribo en todos los movmientos en todos los albaranes asociados el batch_picking_id
        #Los movimientos que no estén incluidos, los paso a otro picking

        error_picking = picking_ids.filtered(lambda x: x.state in ('done', 'cancel') or (
                    x.draft_batch_picking_id and x.draft_batch_picking_id != batch_picking_id))
        if error_picking:
            raise ValidationError(
                _('Albaranes de pedidos en estado inconsistente. {}'.format([x.name for x in error_picking])))
        error_moves = self.filtered(lambda x: x.state in ('done', 'cancel') or (
                    x.draft_batch_picking_id and x.draft_batch_picking_id != batch_picking_id))
        if error_moves:
            raise ValidationError(_('Movimientos en estado inconsistente. {}'.format([x.name for x in error_picking])))

        val = {'draft_batch_picking_id': batch_picking_id.id}
        #escribo en todos los movimientos el nuevo batch picking id
        self.write(val)

        for pick in picking_ids:
            #import ipdb; ipdb.set_trace()
            ##si el albarán no tiene picking se lo escribo
            if pick.draft_batch_picking_id:
                if pick.draft_batch_picking_id != batch_picking_id:
                    raise ValidationError (_('Albaran ya asignado a un grupo'))
            else:
                pick.draft_batch_picking_id = batch_picking_id.id
            ## reviso que movimientos del albaran tengo que reasignar
            pick_moves = pick.move_lines.filtered(lambda x: x.draft_batch_picking_id != pick.draft_batch_picking_id)
            if pick_moves:
                pick_moves.write({'picking_id': False})
                pick_moves._assign_picking()

    @api.multi
    def button_unlink_from_batch(self):
        return self.action_remove_moves_to_batch_picking()

    @api.multi
    def action_add_to_batch_picking(self):


        to_add = self.filtered(lambda x: x.state != 'done' and not x.draft_batch_picking_id).get_affected_moves()
        to_remove = self.filtered(lambda x: x.state != 'done' and  x.draft_batch_picking_id).get_affected_moves()
        if to_add and to_remove:
            raise ValidationError (_('Selección inconsiste. Hay movimientos con y sin batch'))
        if to_remove:
            to_remove.write({'draft_batch_picking_id': False})
        elif to_add:
            ctx = self._context.copy()
            if 'active_domain' in ctx.keys():
                ctx.pop('active_domain')
            obj = self.env['stock.batch.picking.wzd']
            wzd_id = obj.create_from('stock.move', to_add.ids)
            action = wzd_id.get_formview_action()
            action['target'] = 'new'
            return action

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        new_args = expression.normalize_domain(args.copy())
        ctx = self._context.copy()
        if self._context.get('delivery_route_group_id', False):
            group_ids = self.env['delivery.route.path.group'].search(
                [('name', 'ilike', self._context['delivery_route_group_id'])])
            if group_ids:
                route_ids = [('delivery_route_path_id', 'in', group_ids.mapped('route_path_ids').ids)]
                new_args = expression.AND([route_ids, new_args])
        if self._context.get('ghost_qty_done', False):
            ctx.update(ghost_qty_done=False)
            moves = self.env['stock.move'].with_context(ctx).search_read(new_args, ['id'])
            if moves:
                line_ids = [('id', 'in', [x['id'] for x in moves]), ('qty_done', '>', 0)]
                if line_ids:
                    moves_qty = self.env['stock.move.line'].search_read(line_ids, ['move_id'])
                    if moves_qty:
                        new_args = expression.AND([('id', 'in', [x['move_id'][0] for x in moves_qty]), new_args])

        return super(StockMove, self.with_context(ctx)).search(new_args, offset=offset, limit=limit, order=order, count=count)


    @api.multi
    def action_add_to_batch_delivery(self):
        action = self.env.ref('stock_move_selection_wzd.batch_delivery_wzd_act_window').read()[0]
        if self._context.get('object') == 'move':
            self.get_affected_moves().filtered(lambda x:x.batch_delivery_id).write({'batch_delivery_id': False})
            return
        elif self._context.get('object') == 'package':
            if self.result_package_id and self.batch_delivery_id:
                ctx = self._context.copy()
                ctx.update(force_route_vals=True)
                package = self.with_context(ctx).result_package_id
                package.batch_delivery_id= False
                package.move_line_ids.write({'batch_delivery_id': False})

                return
            object = 'package'
        return action

    @api.multi
    def button_reasignar_origen_wzd(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_move_selection_wzd.act_view_move_change_quant_wzd').read()[0]
        if self.id:
            wzd_obj = self.env['move.change.quant.wzd']
            vals = wzd_obj.return_move_vals(self)
            wzd_id = wzd_obj.create(vals)
            ctx = {
                    'lang': 'es_ES',
                    'tz': 'Europe/Madrid',
                    'uid': 5}
            action = wzd_id.with_context(ctx).get_formview_action()
            action['target'] = 'new'

        return action

    @api.multi
    def _return_action_show_moves(self, group_code=''):
        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]
        action['domain'] = self.get_moves_selection_domain(group_code)
        action['views'] = [(tree and tree.id or False, 'tree'),
                           (kanban and kanban.id or False, 'kanban')]
        action['context'] = {group_code if group_code else 'all': True,
                             'show_partner': group_code in ['internal', 'location', 'reposition'],
                             'show_date': group_code in ['incoming', 'outgoing'],
                             'search_default_todo': 1,
                             'search_default_without_pick': 1}
        name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        if name_str:
            action['display_name'] = "---------> {} Moves".format(name_str[0])
        return action

    def get_domain_moves_to_asign(self):
        return self.filtered(lambda x: not x.picking_id and x.state not in ('done', 'cancel', 'draft'))

    @api.multi
    def move_sel_assign_picking(self):

        moves = self.get_domain_moves_to_asign()
        for move in moves:
            move.action_force_assign_picking()
        if moves:
            res = self.env['stock.move']._return_action_show_moves()
            res['context'] = {'search_default_without_pick': 0}
            res['domain'] = [('id', 'in', moves.ids)]
            return res

    def get_domain_moves_to_deasign(self):
        return self.filtered(lambda x: x.picking_id and x.state not in ('done', 'cancel', 'draft'))


    @api.multi
    def move_assign_batch_delivery(self):
        ## Solo para picking_type_id
        not_moves = self.filtered(lambda x: x.picking_type_id.code != 'outgoing')

        if self.filtered(lambda x: x.batch_delivery_id):
            raise ValidationError(_('Algunos movimientos ya tienen orden de carga seleccionada'))
        vals = {}

        if len(self.mapped('shipping_type')) == 1:
            vals.update(default_shipping_type = self[0].shipping_type)
        if len(self.mapped('delivery_route_path_id')) == 1:
            vals.update(default_delivery_route_path_id = self[0].delivery_route_path_id.id)
        if len(self.mapped('carrier_id')) == 1:
            vals.update(default_carrier_id = self[0].carrier_id.id)

        vals.update(default_move_ids=[(6,0, self.ids)])
        vals.update(default_date=min(self.mapped('date_expected')))

        ctx = self._context.copy()
        ctx.update(vals)

        action = self.env.ref(
            'stock_move_selection_wzd.batch_delivery_wzd_act_window').read()[0]
        return action

    @api.multi
    def action_tree_manage_pack(self):
        if any(x.state == 'done' for x in self):
            raise ValidationError (_('No puedes asignar un paquete a un movimiento hecho. Deberás empaquetar posteriormente'))

        if self.result_package_id:
            package = self.result_package_id
            self.result_package_id = False
            return True
        else:
            wzd_id = self.env['stock.move.pack.wzd'].create_from_moves(self)
            action = self.env.ref(
                'stock_move_selection_wzd.view_stock_move_pack_wzd_act_window').read()[0]
            action['res_id'] = wzd_id.id
            return action

    @api.multi
    def move_de_sel_assign_picking(self):
        self.write({'picking_id': False})
        self.mapped('move_line_ids').write({'picking_id': False})
        res = self._return_action_show_moves()
        res['context'] = {'search_default_without_pick': 1}
        res['domain'] = [('id', 'in', self.ids)]
        return res

    @api.multi
    def write(self, vals):
        #if 'picking_id' in vals:
        #    self.mapped('move_line_ids').write({'picking_id': vals['picking_id']})
        return super().write(vals)

    @api.multi
    def set_package_id_to_lines(self):
        for move in self:
            move.mapped('move_line_ids').write({'result_package_id': move.package_id.id})

    @api.multi
    @api.depends('move_line_ids.package_id')
    def get_package_id_from_line(self):
        for move in self:
            package_id = move.move_line_ids.mapped('package_id')
            move.package_id = package_id and package_id[0] or False

    @api.multi
    def set_result_package_id_to_lines(self):

        for move in self:
            move.mapped('move_line_ids').write({'result_package_id': move.result_package_id.id})

    @api.multi
    @api.depends('move_line_ids.result_package_id')
    def get_result_package_id_from_line(self):

        for move in self:
            result_package_id = move.move_line_ids.mapped('result_package_id')
            move.result_package_id = result_package_id and result_package_id[0] or False

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        domain += [('batch_picking_id', '=', False), ('draft_batch_picking_id', '=', False)]
        return domain

    def _action_done(self):
        res = super()._action_done()
        for move in self.filtered(lambda x: x.sga_state not in ('no_integrated', 'done')):
            move.sga_state = 'done'
        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty=qty)
        if self.picking_type_id.parent_id:
            res.update({
                'picking_type_id': self.picking_type_id.parent_id.id,
                'location_id': self.picking_type_id.parent_id.default_location_src_id.id,
                'location_dest_id': self.picking_type_id.parent_id.default_location_dest_id.id,
            })
        return res

    @api.multi
    def _force_assign_create_lines(self):
        moves = self.filtered(lambda x: x.state in ('confirmed', 'partially_available'))
        for move in moves:
            move._do_unreserve()
            move._action_assign()
            if move.state == 'assigned':
                continue
            missing_reserved_uom_quantity = move.product_uom_qty - move.reserved_availability
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity,
                                                                           move.product_id.uom_id,
                                                                           rounding_method='HALF-UP')
            self.env['stock.move.line'].create(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
            move.write({'state': 'assigned'})




    def get_batch_domain(self):
        domain = super().get_batch_domain()
        domain += [('batch_delivery_id', '=', False)]
        return domain

