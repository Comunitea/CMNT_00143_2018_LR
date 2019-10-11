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
    #draft_move_lines_id = fields.One2many('stock.move.line', 'draft_batch_picking_id', string='Líneas de Movimientos')

    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", compute="get_sga_state")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)
    code = fields.Selection(related='picking_type_id.code')
    excess = fields.Boolean(string='Franquicia')
    date_done = fields.Datetime('Realizado', copy=False, help="Fecha de transferencia")

    def get_excess_domain(self):
        from_time = self.env['stock.picking.type'].get_excess_time()
        domain = [('date', '>=', from_time),
                  ('state', 'in', ('ready', 'done'))]
        return domain

    @api.multi
    def action_assign(self):
        res = super().action_assign()
        #self.filtered(lambda x: x.code == 'outgoing').get_transport_excess()
        return res



    @api.multi
    def alternate_draft_ready(self):
        for batch in self:
            if batch.state == 'ready':
                batch.state == 'draft'
            elif batch.state =='draft':
                batch.state == 'ready'

    @api.multi
    @api.depends('state', 'move_lines.shipping_type', 'move_lines.delivery_route_path_id', 'move_lines.carrier_id',
                 'draft_move_lines.shipping_type', 'draft_move_lines.delivery_route_path_id',
                 'draft_move_lines.carrier_id')
    def compute_route_fields(self):
        done_batch = self.filtered(lambda x:x.state == 'done')
        draft_batch = self.filtered(lambda x:x.state != 'done')
        super(StockBatchPicking, done_batch).compute_route_fields()

        for batch in draft_batch:
            moves = batch.draft_move_lines
            if moves:
                shipping_type_ids = []
                for move in moves:
                    if move.shipping_type in shipping_type_ids:
                        continue
                    shipping_type_ids.append(move.shipping_type)
                if shipping_type_ids[0] and len(shipping_type_ids) == 1:
                    batch.shipping_type = shipping_type_ids[0]
                delivery_route_path_ids = moves.mapped('delivery_route_path_id')
                if len(delivery_route_path_ids) == 1:
                    batch.delivery_route_path_id = delivery_route_path_ids[0]
                carrier_ids = moves.mapped('carrier_id')
                if len(carrier_ids) == 1:
                    batch.carrier_id = carrier_ids[0]

    def check_allow_change_route_fields(self):
        super().check_allow_change_route_fields()
        if any((move.state != 'done' and move.batch_delivery_id) for move in self.draft_move_lines) and not self._context.get('force_route_vals', False):
            raise ValidationError(_('No puedes cambiar en movimientos de una orden de carga'))
        return True

    @api.multi
    def set_route_fields(self):
        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        for batch in self.with_context(ctx):
            batch.check_allow_change_route_fields()
            moves = batch.move_lines + batch.draft_move_lines
            moves.write({
                'shipping_type': batch.shipping_type,
                'delivery_route_path_id': batch.delivery_route_path_id.id,
                'carrier_id': batch.carrier_id.id
            })

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
            moves = batch.get_batch_moves_to_transfer()
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
        rs = super().unlink()

    @api.multi
    def action_transfer(self):
        """
        """
        self.filtered(lambda x: x.picking_type_id.code == 'outgoing').compute_route_fields()

        effective = self.filtered(lambda x: x.draft_move_lines)
        normal = self.filtered(lambda x: not x.draft_move_lines and x.state != 'done')
        if effective:
            for batch in effective:
                moves = batch.get_batch_moves_to_transfer()
                if all(x.qty_done == 0.00 for x in moves.mapped('move_line_ids')):
                    for ml in moves.mapped('move_line_ids'):
                        ml.qty_done = ml.product_uom_qty
                done_moves = moves.filtered(lambda x: x.state in ('assigned', 'partially_available') and x.quantity_done > 0)
                unlink_moves = moves-done_moves
                unlink_moves.write({'draft_batch_picking_id': False})
                done_moves._action_done()
                picks = done_moves.mapped('picking_id')
                picks.action_done()
                done_moves.write({'batch_picking_id': batch.id})
                batch.verify_state()
                backorders = unlink_moves.mapped('picking_id')
                message = _(
                    "Se ha validado el batch por "
                    "<a href=# data-oe-model=res.user data-oe-id=%d>%s</a> <ul>"
                    ) % (self.env.user.user_id.id, self.env.user.display_name)

                if picks:
                    pick_message = '<ul>Albaranes:'
                    message = "{}{}".format(message, pick_message)
                    for pick in picks:
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
