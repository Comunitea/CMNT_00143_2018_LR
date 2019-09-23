# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .stock_picking_type import PICKING_TYPE_GROUP
from .stock_picking_type import SGA_STATES

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
                                 store=True)
    result_package_id = fields.Many2one('stock.quant.package', 'Paquete destino',
                                        inverse='set_result_package_id_to_lines',
                                        compute="get_result_package_id_from_line",
                                        store=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lote')
    dunmy_picking_id = fields.Many2one('stock.picking', 'Transfer Reference', store=False)
    sga_integrated = fields.Boolean(related="picking_type_id.sga_integrated")
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado")
    batch_delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga', store=True)
    batch_picking_id = fields.Many2one(related='picking_id.batch_picking_id', string='Grupo', store=True)
    draft_batch_picking_id = fields.Many2one('stock.batch.picking', string='Grupo')
    batch_id = fields.Many2one('stock.batch.picking', compute="get_effective_batch_id", inverse='set_effective_batch_id', string='Grupo')
    code = fields.Selection(related='picking_type_id.code')
    group_code = fields.Selection(related='picking_type_id.group_code')
    decoration = fields.Char(compute = get_color_status)



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
        if package:
            vals = package.update_info_route_vals()
            if package.batch_delivery_id:
                vals.update(batch_delivery_id=package.batch_delivery_id.id)
            self.write(vals)

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
        return result_package_ids.mapped("move_line_ids").mapped('move_id')

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
    def action_add_to_batch_picking(self):
        to_add = self.filtered(lambda x: not x.draft_batch_picking_id).get_affected_moves()
        to_remove = self.filtered(lambda x: x.draft_batch_picking_id).get_affected_moves()
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


            action = self.env.ref('stock_move_selection_wzd.open_view_create_batch_picking').read()[0]
            action['res_id'] = wzd_id.id
            return action

    @api.multi
    def action_add_to_batch_delivery(self):
        action = self.env.ref('stock_move_selection_wzd.batch_delivery_wzd_act_window').read()[0]
        if self._context.get('object') == 'move':
            self.get_affected_moves().filtered(lambda x:x.batch_delivery_id).write({'batch_delivery_id': False})
            return
            object='move'
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

        action = self.env.ref(
            'stock_move_selection_wzd.act_view_move_change_quant_wzd').read()[0]
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
        if not_moves:
            raise ValidationError (_('No hay movimientos de salida seleccionados'))
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

        if self.result_package_id:
            package = self.result_package_id
            self.result_package_id = False
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
        if 'picking_id' in vals:
            self.mapped('move_line_ids').write({'picking_id': vals['picking_id']})
        return super().write(vals)

    def set_package_id_to_lines(self):
        for move in self:
            move.mapped('move_line_ids').write({'result_package_id': move.package_id.id})

    @api.depends('move_line_ids.package_id')
    def get_package_id_from_line(self):
        for move in self:
            move.package_id = move.move_line_ids.mapped('package_id')

    def set_result_package_id_to_lines(self):
        for move in self:
            move.mapped('move_line_ids').write({'result_package_id': move.result_package_id.id})

    @api.depends('move_line_ids.result_package_id')
    def get_result_package_id_from_line(self):
        for move in self:
            move.result_package_id = move.move_line_ids.mapped('result_package_id')

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        return domain

    def _action_done(self):
        return super()._action_done()


