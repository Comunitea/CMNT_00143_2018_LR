# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError


class StockBatchDelivery(models.Model):
    """ This object allow to manage multiple stock.batch.picking
    """

    _inherit = ['info.route.mixin']
    _name = 'stock.batch.delivery'

    @api.depends('move_lines.date_expected')
    @api.multi
    def _get_dates(self):
        for batch in self:
            batch.date_expected = min(move.date_expected for move in batch.move_lines)

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
        print (domain)
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
    carrier_id = fields.Many2one("delivery.carrier", string="Forma de envío")
    batch_ids = fields.One2many('stock.batch.picking', 'batch_delivery_id', 'Grupo',
                                states={
                                    'draft': [('readonly', False)],
                                    'ready': [('readonly', False)]
                                },
                                readonly=True,
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

    @api.multi
    def _get_picking_ids(self):
        for out_batch in self:

            out_batch.move_lines = self.env['stock.move'].search([('batch_delivery_id', '=', out_batch.id)])
            out_batch.picking_ids = out_batch.move_lines.mapped('picking_id')
            out_batch.move_lines_ids = out_batch.move_lines.mapped('move_line_ids')
            out_batch.partner_ids = out_batch.move_lines.mapped('partner_id')

            out_batch.count_picking_ids = len(out_batch.picking_ids)
            out_batch.count_move_lines = len(out_batch.move_lines)
            out_batch.count_package_ids = len(out_batch.package_ids)

    @api.multi
    def action_transfer(self):
        for batch in self:
            batch.package_ids.action_done()
            batch.picking_ids.action_done()

    @api.multi
    def action_transfer(self):
        """ Make the transfer for all active pickings in these batches
        and set state to done all picking are done.
        """
        batches = self.get_not_empties()
        for batch in batches:
            if not batch.verify_state():
                batch.active_picking_ids.force_transfer(
                    force_qty=all(
                        operation.qty_done == 0
                        for operation in batch.move_line_ids
                    )
                )


    @api.multi
    def action_view_batch_ids(self):
        """This function returns an action that display existing pickings of
        given batch picking.
        """
        self.ensure_one()

        action = self.env.ref('stock_batch_picking.action_stock_batch_picking_tree').read([])[0]
        action['domain'] = [('id', 'in', self.batch_ids.ids)]
        return action

    @api.multi
    def action_view_packages_ids(self):
        """This function returns an action that display existing packages of
        given batch picking.
        """
        self.ensure_one()
        action = self.env.ref('stock.action_package_view').read([])[0]
        action['domain'] = [('id', 'in', self.package_ids.ids)]
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

