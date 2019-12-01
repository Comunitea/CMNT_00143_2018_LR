# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError, ValidationError


class StockPackageBatch(models.Model):
    """ This object allow to manage multiple stock.picking at the same time.
    """

    _inherit = ['info.route.mixin']
    _name = 'stock.package.batch'

    name = fields.Char(
        'Name',
        required=True, index=True,
        copy=False, unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'stock.move.batch'
        ),
    )
    partner_id = fields.Many2one('res.partner', string='Delivery Address')

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

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')

    expected_date = fields.Date(
        'Date',
        required=True, readonly=True,
        states={
            'draft': [('readonly', False)],
            'ready': [('readonly', False)]
        },
        default=fields.Date.context_today,
        help='date on which the batch picking is to be processed'
    )
    date_done = fields.Date(  'Date',
        required=True, readonly=True,
        default=fields.Date.context_today,
        help='date on which the batch picking is processed'
    )

    picker_id = fields.Many2one(
        'res.users', 'Picker',
        readonly=True, index=True,
        states={
              'draft': [('readonly', False)],
            'ready': [('readonly', False)]
        },
        help='the user who prepare the moves'
    )
    package_ids = fields.One2many('stock.quant.package', 'batch_delivery_id', 'Batch picking', )
    batch_ids = fields.One2many('stock.batch.picking', 'batch_delivery_id', 'Batch picking',
                                domain=[('picking_type_id.group_code', '=', 'outgoing'), ('state', 'in', ('assigned', 'done'))])

    picking_ids = fields.One2many(
        'stock.picking', 'batch_picking_id', 'Pickings',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_get_picking_ids',
        help='List of picking related to this batch.'
    )

    active_picking_ids = fields.One2many(
        'stock.picking', 'batch_picking_id', 'Pickings',
        readonly=True,
        domain=[('state', 'not in', ('cancel', 'done'))],
    )
    notes = fields.Text('Notes', help='free form remarks')

    move_lines = fields.One2many(
        'stock.move',
        'batch_delivery_id',
        readonly=True,
        string='Related stock moves',
    )

    move_line_ids = fields.Many2many(
        'stock.move.line',
        string='Related pack operations',
    )

    entire_package_ids = fields.Many2many(
        comodel_name='stock.quant.package',
        compute='_compute_entire_package_ids',
        help='Those are the entire packages of a picking shown in the view of '
             'operations',
    )

    entire_package_detail_ids = fields.Many2many(
        comodel_name='stock.quant.package',
        compute='_compute_entire_package_ids',
        help='Those are the entire packages of a picking shown in the view of '
             'detailed operations',
    )

    @api.depends('picking_ids')
    def _compute_move_lines(self):
        for batch in self:
            batch.move_lines = batch.picking_ids.mapped("move_lines")

    @api.depends('picking_ids')
    def _compute_move_line_ids(self):
        for batch in self:
            batch.move_line_ids = batch.picking_ids.mapped(
                'move_line_ids'
            )

    @api.depends('picking_ids')
    def _compute_entire_package_ids(self):
        for batch in self:
            batch.update({
                'entire_package_ids': batch.picking_ids.mapped(
                    'entire_package_ids'),
                'entire_package_detail_ids': batch.picking_ids.mapped(
                    'entire_package_detail_ids'),
            })

    def open_tree_to_add(self):
        model = self._context.get('model', 'stock.move')
        if not self.picking_type_id:
            raise ValidationError (_('Necesitas un tipo de albarán para generar el lote'))


        states = ('confirmed', 'assigned', 'partially_available')
        domain = [('pìcking_id', '!=', False), ('draft_batch_picking_id', '=', False),
                  ('picking_type_id', '=', self.picking_type_id.id), ('state', 'in', states)]

        if self.delivery_route_path_ids:
            domain += ['|', ('delivery_route_path_id', 'in', self.delivery_route_path_ids.ids), ('delivery_route_path_id', '=', False)]

        if self.shipping_type_ids:
            domain += [('shipping_type', '=', self.shipping_type_ids)]

        if self.payment_term_ids.ids:
            domain += ['|', ('payment_term_id', 'in', self.payment_term_ids.ids),
                       ('payment_term_ids', '=', False)]

        if model == 'stock.move':
            objs = self.search_read(domain, ['id'])
            active_ids = [x['id'] for x in objs]
        elif model == 'stock.picking':
            objs = self.search_read(domain, ['picking_id'])
            active_ids = [x['picking_id'][0] for x in objs if objs['picking_id']]

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


        return



    def get_not_empties(self):
        """ Return all batches in this recordset
        for which picking_ids is not empty.

        :raise UserError: If all batches are empty.
        """
        if not self.mapped('picking_ids'):
            if len(self) == 1:
                message = _('This Batch has no pickings')
            else:
                message = _('These Batches have no pickings')

            raise UserError(message)

        return self.filtered(lambda b: len(b.picking_ids) != 0)

    def verify_state(self, expected_state=None):
        """ Check if batches states must be changed based on pickings states.

        If all pickings are canceled, batch must be canceled.
        If all pickings are canceled or done, batch must be done.
        If all pickings are canceled or done or *expected_state*,
            batch must be *expected_state*.

        :return: True if batches states has been changed.
        """
        expected_states = {'done', 'cancel'}
        if expected_state is not None:
            expected_states.add(expected_state)

        all_good = True
        for batch in self.filtered(lambda b: b.state not in expected_states):
            states = set(batch.mapped('picking_ids.state'))
            if not states or states == {'cancel'}:
                batch.state = 'cancel'
            elif states == {'done'} or states == {'done', 'cancel'}:
                batch.state = 'done'

            elif states.issubset(expected_states):
                batch.state = expected_state

            else:
                all_good = False

        return all_good

    @api.multi
    def action_cancel(self):
        """ Call action_cancel for all batches pickings
        and set batches states to cancel too.
        """

        for batch in self:
            if not batch.picking_ids:
                batch.write({'state': 'cancel'})
            else:
                if not batch.verify_state():
                    batch.picking_ids.action_cancel()

    @api.multi
    def action_assign(self):
        """ Check if batches pickings are available.
        """
        batches = self.get_not_empties()
        if not batches.verify_state('assigned'):
            batches.mapped('active_picking_ids').action_assign()

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
    def remove_undone_pickings(self):
        """ Remove of this batch all pickings which state is not done / cancel.
        """
        self.mapped('active_picking_ids').write({'batch_picking_id': False})
        self.verify_state()

    @api.multi
    def action_view_stock_picking(self):
        """This function returns an action that display existing pickings of
        given batch picking.
        """
        self.ensure_one()
        pickings = self.mapped('picking_ids')
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        return action
