# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import ValidationError

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

from .stock_picking_type import SGA_STATES

class StockBatchPicking(models.Model):

    _inherit = ['stock.batch.picking', 'mail.thread', 'mail.activity.mixin']
    _name = 'stock.batch.picking'

    @api.multi
    def _get_draft_move_lines(self):
        for batch_picking_id in self:
            if batch_picking_id.picking_type_id.sga_integrated:
                batch_picking_id.draft_move_lines = batch_picking_id.move_lines.filtered(
                    lambda x: x.sga_state not in ('ready', 'done', 'cancel') and x.reserved_availability > 0)
            else:
                batch_picking_id.draft_move_lines = batch_picking_id.move_lines.filtered(
                    lambda x: x.reserved_availability > 0)

    batch_delivery_id = fields.Many2one('stock.batch.delivery', string="Delivery batch")
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking type', required=True, readonly=True, states={'draft': [('readonly', False)]},)
    draft_move_lines = fields.One2many('stock.move', 'draft_batch_picking_id', string='Movimientos')
    draft_picking_ids = fields.One2many('stock.picking', 'draft_batch_picking_id', string='Albaranes')

    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", compute="get_sga_state")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)
    code = fields.Selection(related='picking_type_id.code')
    excess = fields.Boolean(string='Franquicia')
    date_done = fields.Datetime('Realizado', copy=False, help="Fecha de transferencia")
    ready_to_transfer = fields.Boolean('Listo para transferir', compute="compute_ready_to_transfer")
    count_move_lines = fields.Integer('Nº líneas', compute="_get_nlines")

    @api.depends('picking_ids', 'draft_picking_ids')
    def _compute_move_lines(self):
        for batch in self.filtered(lambda x: not x.draft_move_lines):
            batch.move_lines = batch.picking_ids.mapped("move_lines")

        for batch in self.filtered(lambda x: x.draft_move_lines):
            batch.move_lines = batch.draft_move_lines

    @api.multi
    def compute_ready_to_transfer(self):
        for batch in self:
            moves = batch.draft_move_lines or batch.move_lines
            if moves and all(x.state in ('assigned', 'partially_available') for x in moves):
                batch.ready_to_transfer = True
            else:
                batch.ready_to_transfer = False



    @api.multi
    def _get_nlines(self):
        for pick in self:
            if pick.draft_move_lines and pick.state != 'done':
                pick.count_move_lines = len(pick.draft_move_lines)
            else:
                pick.count_move_lines = len(pick.move_lines)

    def get_excess_domain(self):
        from_time = self.env['stock.picking.type'].get_excess_time()
        domain = [('date', '>=', from_time),
                  ('state', 'in', ('ready', 'done'))]
        return domain

    @api.multi
    def alternate_draft_ready(self):
        for batch in self:
            if batch.state == 'ready':
                batch.state == 'draft'
            elif batch.state =='draft':
                batch.state == 'ready'

    def check_allow_change_route_fields(self):
        super().check_allow_change_route_fields()
        if any((move.state != 'done' and move.batch_delivery_id) for move in self.draft_move_lines) and not self._context.get('force_route_vals', False):
            raise ValidationError(_('No puedes cambiar en movimientos de una orden de carga'))
        return True



    @api.multi
    @api.depends('draft_move_lines.sga_state')
    def get_sga_state(self):
        for batch in self:
            lines = batch.draft_move_lines
            batch.sga_state = self.env['stock.picking.type'].get_parent_state(lines)

    def get_batch_moves_to_transfer(self):
        return self.draft_move_lines

    @api.multi
    def set_as_sga_done(self):
        for batch in self:
            moves = batch.get_batch_moves_to_transfer().filtered(lambda x: x.quantity_done > 0.00)
            moves.write({'sga_state': 'done'})

    @api.depends('picking_ids.partner_id', 'draft_move_lines.partner_id')
    @api.multi
    def get_partner_id(self):
        for batch in self:
            if batch.picking_ids:
                partner_id = batch.picking_ids.mapped('partner_id')
            else:
                partner_id = batch.draft_move_lines.mapped('partner_id')
            if len(partner_id) == 1:
                batch.partner_id = partner_id[0]
            else:
                batch.partner_id = False

    @api.multi
    def unlink(self):
        if self.mapped('batch_delivery_id'):
            self.draft_move_lines.batch_delivery_id
            raise ValidationError(_('No puedes eliminar un grupo que ya está en una orden de carga. Priemro debes sacarlo de la orden de carga'))
        return super().unlink()

    @api.multi
    def set_as_done(self):
        for batch in self:
            moves = batch.get_batch_moves_to_transfer()
            for move in moves:
                if move.state in ('assigned', 'partially_available'):
                    move._do_unreserve()

            if all(x.qty_done == 0.00 for x in moves.mapped('move_line_ids')) and False:
                for ml in moves.mapped('move_line_ids'):
                    ml.qty_done = ml.product_uom_qty

    @api.multi
    def force_assign_create_lines(self):
        for batch in self:
            batch.draft_move_lines._force_assign_create_lines()
            batch.move_lines._force_assign_create_lines()


    @api.multi
    def action_transfer(self):
        """
        """
        #self.filtered(lambda x: x.picking_type_id.code == 'outgoing').compute_route_fields()
        effective = self.filtered(lambda x: x.draft_move_lines)
        normal = self.filtered(lambda x: not x.draft_move_lines and x.state != 'done')
        if effective:
            for batch in effective:
                moves = batch.get_batch_moves_to_transfer()
                #if all(x.qty_done == 0.00 for x in moves.mapped('move_line_ids')) and False:
                #    for ml in moves.mapped('move_line_ids'):
                #        ml.qty_done = ml.product_uom_qty
                moves.write({'draft_batch_picking_id': False})
                moves_to_do = moves.filtered(lambda x: x.state in ('partially_available', 'assigned')).mapped('move_line_ids')
                for ml in moves_to_do:
                    ml.qty_done = ml.product_uom_qty
                picks_to_transfer = moves.mapped('picking_id')
                if not picks_to_transfer:
                    continue
                picks_to_transfer.action_done()
                picks_to_transfer.write({'batch_picking_id': batch.id,
                                         'draft_batch_picking_id': False})
                batch.verify_state()

                back_domain = [('backorder_id', 'in', picks_to_transfer.ids), ('state', '!=', 'cancel')]
                backorders = self.env['stock.picking'].search(back_domain)
                message = _(
                    "Se ha validado el batch por "
                    "<a href=# data-oe-model=res.user data-oe-id=%d>%s</a> <ul>"
                    ) % (self.env.user.user_id.id, self.env.user.display_name)

                if picks_to_transfer:
                    pick_message = '<ul>Albaranes:'
                    message = "{}{}".format(message, pick_message)
                    for pick in picks_to_transfer:
                        pick_message = "<li><a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>{}</li>"% (pick.id, pick.name)
                        message = "{}{}".format(message, pick_message)
                    message = "{}</ul>".format(message)

                if backorders:
                    pick_message = '<ul>Pendientes:'
                    message = "{}{}".format(message, pick_message)
                    for pick in backorders:
                        pick_message = "<li><a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>{}</li>"% (pick.id, pick.name)
                        message = "{}{}".format(message, pick_message)
                    message = "{}</ul>".format(message)
                batch.message_post(message)
                batch.write({'state': 'done',
                             'date_done': fields.Datetime.now()})

        if normal.mapped('picking_ids'):
            return super(StockBatchPicking, normal).action_transfer()


    @api.onchange('picking_ids')
    def onchange_picking_ids(self):
        for batch in self:
            if all(pick.picking_type_id == batch.picking_type_id for pick in batch.picking_ids):
                continue
            raise ValidationError ("Todos los albaranes deben de ser del mismo tipo ({})".format(batch.picking_type_id.name))

    @api.multi
    def write(self, vals):
        return super().write(vals)

    @api.multi
    def action_see_packages(self):
        self.ensure_one()
        action = self.env.ref('stock.action_package_view').read()[0]
        packages = self.move_line_ids.mapped('result_package_id')
        action['domain'] = [('id', 'in', packages.ids)]
        return action


    @api.multi
    def action_see_moves(self):

        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({
            'default_domain': [('batch_picking_id', '=', self.id), ('state', 'not in', ('cancel', 'draft'))],
            'dest_model': 'stock.move',
            'this_context': True,
        })
        if self.picking_type_id.code == 'internal':
            ctx.update({
                'search_default_by_sale_id': True
            })
        elif self.picking_type_id.code == 'outgoing':
            ctx.update({
                'search_default_by_sale_id': True
            })
        else:
            ctx.update({
                'search_default_by_sale_id': True
            })
        if self.state == 'done':
            ctx.update(hide_state=True)
            ctx.update(hide_reserved_availability=True)

        action = self.with_context(ctx).picking_type_id.get_action_tree()
        action['domain'] = [('batch_picking_id', '=', self.id)]
        action['context'] = ctx
        return action


    @api.multi
    def batch_printing(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise ValidationError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return self.env.ref('stock_move_selection_wzd.delivery_batch_report').with_context(active_ids=active_ids, active_model='stock.batch.picking', pickings=pickings).report_action([])

    def action_send_to_sga(self):
        return self.send_to_sga()

    @api.multi
    def send_to_sga(self):
        for batch in self:
            lines =  batch.draft_move_lines
            sga_done_vals = {'sga_state': 'pending'}
            lines.write(sga_done_vals)
            ##PARA HEREDAR EN ULMA Y ADAIA
            message = _(
                "Se ha enviado a los sistemas de SGA "
                "<a href=# data-oe-model=stock.batch.picking data-oe-id=%d>%s</a> <ul>") % (batch.id, batch.name)

            batch_message = message
            for pick in batch.draft_picking_ids:
                batch_message = '{} <li> El albarán {} ha sido incluido en el lote</li>'.format(batch_message, "<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> (%s)"%(pick.id, pick.name, pick.origin))


                not_sga_lines = pick.move_lines.filtered(lambda x: x.state != 'pending')
                if not_sga_lines:
                    continue
                lines_str = '<ul>'
                for line in not_sga_lines:
                    lines_str = '{} <li> La línea de {} no se ha enviado al SGA </li>'.format(lines_str, "<a href=# data-oe-model=stock.batch.picking data-oe-id=%d>%s</a>"%(line.id, line.name))
                lines_str = '{}</ul>'.format(lines_str)
                pick.message_post('{}{}'.format(message, lines_str))


            batch_message = '{}</ul>'.format(batch_message)
            batch.message_post(batch_message)
            batch.draft_picking_ids.write({'sga_state': 'pending'})
            batch.sga_state = 'pending'

        return True

    @api.multi
    def read_from_sga(self):
        return True
