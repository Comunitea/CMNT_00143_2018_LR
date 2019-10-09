# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError,ValidationError


class StockBatchDelivery(models.Model):
    """ This object allow to manage multiple stock.batch.delivery
    """

    _inherit = ['info.route.mixin', 'mail.thread', 'mail.activity.mixin']
    _name = 'stock.batch.delivery'

    @api.depends('move_lines.date_expected')
    @api.multi
    def _get_dates(self):
        for batch in self:
            if batch.move_lines:
                batch.date_expected = min((move.date_expected or move.date) for move in batch.move_lines)

    @api.onchange('date_expected')
    def _set_dates(self):
        for batch in self:
            batch.move_lines.write({'date_expected': batch.date_expected})

    @api.model
    def _get_batch_domain(self):
        bp = self and self[0]
        if bp:
            domain = [('state', 'in', ('assigned', 'done')), ('picking_type_id', '=', bp.picking_type_id.id)]

        else:
            domain=[('state', 'in', ('assigned', 'done'))]
        return domain

    name = fields.Char(
        'Name',
        required=True, index=True,
        copy=False, unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'stock.batch.delivery'
        ),
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')],
        string='State',
        readonly=True, index=True, copy=False,
        default='draft',
        help='the state of the batch packages. '
        'Workflow is draft -> assigned -> done or cancel'
    )
    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo de operación')
    date_expected = fields.Date(
        'Fecha prevista',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'ready': [('readonly', False)]
        },
        compute=_get_dates,
        inverse=_set_dates,
        help='date on which the batch picking is to be processed'
    )
    date_done = fields.Date(  'Date',
        required=True, readonly=True,
        default=fields.Date.context_today,
        help='date on which the batch picking is processed'
    )
    picker_id = fields.Many2one(
        'res.users', 'Operario',
        readonly=True, index=True,
        states={
            'ready': [('readonly', False)]
        },
        help='the user who prepare this batch'
    )
    batch_ids = fields.One2many('stock.batch.picking', 'batch_delivery_id', 'Grupo',
                                states={
                                    'draft': [('readonly', False)],
                                    'ready': [('readonly', False)]
                                },
                                readonly=True,
                                compute = '_get_picking_ids',
                                domain=_get_batch_domain)
    picking_ids = fields.One2many(
        'stock.picking', string='Albaranes',
        compute='_get_picking_ids',
        help='List of picking related to this batch.'
    )
    count_picking_ids = fields.Integer('Nº albaranes', compute='_get_picking_ids')
    move_lines = fields.One2many(
        'stock.move',
        string='Movimientos',
        compute='_get_picking_ids',
        help='List of picking related to this batch.'
    )
    count_move_lines = fields.Integer('Nº líneas', compute='_get_picking_ids')
    move_line_ids = fields.One2many(
        'stock.move.line',
        string='Operaciones',
        compute='_get_picking_ids',
        help='List of picking related to this batch.'

    )
    partner_ids = fields.One2many('res.partner', compute='_get_picking_ids', string="Empresa")
    package_ids = fields.One2many(
        'stock.quant.package', 'batch_delivery_id',
        string='Paquetes',
        help='Those are the entire packages of a picking shown in the view of '
             'operations',
    )
    count_package_ids = fields.Integer('Nº paquetes', compute='_get_picking_ids')
    notes = fields.Text('Notas', help='free form remarks')

    driver_id = fields.Many2one('res.partner', string='Conductor',
                                      help='Carrier driver for this batch picking.',
                                      domain="[('route_driver', '=', True)]")
    plate_id = fields.Many2one('delivery.plate', string='Matrícula', help='Plate for this batch picking.')

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", compute='compute_route_fields',
                                 inverse='set_route_fields', store=True)
    shipping_type = fields.Selection(compute='compute_route_fields', inverse='set_route_fields', store=True)
    delivery_route_path_id = fields.Many2one('delivery.route.path', compute='compute_route_fields',
                                           inverse='set_route_fields', store=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)

    @api.multi
    @api.depends('state', 'move_lines.shipping_type', 'move_lines.delivery_route_path_id', 'move_lines.carrier_id')
    def compute_route_fields(self):
        for batch in self:
            moves = batch.move_lines
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
        if any(move.state == 'done' for move in self.move_lines) and not self._context.get(
                'force_route_vals', False):
            raise ValidationError(_('No puedes cambiar en movimientos de una orden de carga'))
        return True

    @api.multi
    def set_route_fields(self):
        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        for batch in self.with_context(ctx):
            batch.check_allow_change_route_fields()
            moves = batch.move_lines
            moves.write({
                'shipping_type': batch.shipping_type,
                'delivery_route_path_id': batch.delivery_route_path_id.id,
                'carrier_id': batch.carrier_id.id
            })

    @api.multi
    def _get_picking_ids(self):
        for out_batch in self:

            out_batch.move_lines = self.env['stock.move'].search([('batch_delivery_id', '=', out_batch.id)])
            out_batch.picking_ids = out_batch.move_lines.mapped('picking_id')
            out_batch.batch_ids = out_batch.move_lines.mapped('batch_id')
            out_batch.move_lines_ids = out_batch.move_lines.mapped('move_line_ids')
            out_batch.partner_ids = out_batch.move_lines.mapped('partner_id')

            out_batch.count_picking_ids = len(out_batch.picking_ids)
            out_batch.count_move_lines = len(out_batch.move_lines)
            out_batch.count_package_ids = len(out_batch.package_ids)

    @api.multi
    def action_transfer(self):
        for batch in self.filtered(lambda x:x.state=='ready'):
            batch.batch_ids.action_transfer()
            batch.state = 'done'

    @api.multi
    def action_transfer_bis(self):
        """ Make the transfer for all active pickings in these batches
        and set state to done all picking are done.
        """
        #batches = self.get_not_empties()
        for batch in self:
            if not batch.verify_state():
                batch.active_picking_ids.force_transfer(
                    force_qty=all(
                        operation.qty_done == 0
                        for operation in batch.move_line_ids
                    )
                )


    @api.multi
    def action_confirm(self):
        self.write({'state': 'ready'})

    @api.multi
    def action_view_stock_package(self):
        """This function returns an action that display existing packages of
        given batch picking.
        """
        self.ensure_one()
        action = self.env.ref('stock.action_package_view').read([])[0]
        action['domain'] = [('id', 'in', self.package_ids.ids)]
        return action

    @api.multi
    def action_view_stock_batch_picking(self):
        batch_ids = self.move_lines.mapped("draft_batch_picking_id")
        self.ensure_one()
        action = self.env.ref('stock_batch_picking.action_stock_batch_picking_tree').read([])[0]
        action['domain'] = [('id', 'in', batch_ids.ids)]
        return action

    @api.multi
    def action_view_stock_move(self):
        self.ensure_one()
        action = self.env.ref('stock_move_selection_wzd.stock_move_sel_action2').read([])[0]
        action['domain'] = [('id', 'in', self.move_lines.ids)]
        action['context'] = self.move_lines and self.move_lines[0].picking_type_id.update_context() or {}
        return action


    @api.multi
    def print_rda_delivery(self):
        raise UserError(_('No implementado.'))
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return self.env.ref('adr_product.delivery_batch_adr_report').with_context(active_ids=active_ids,
                                                                                      active_model='stock.batch.picking',
                                                                                      pickings=pickings).report_action(
                [])

