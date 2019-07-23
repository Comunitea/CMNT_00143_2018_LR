# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockBatchPickingWzd(models.TransientModel):
    """Create a stock.batch.picking from stock.picking
    """

    _name = 'stock.batch.picking.wzd'
    _description = 'Batch Picking Creator'


    batch_id = fields.Many2one('stock.batch.picking', 'Batch picking')
    date = fields.Date(
        'Date', required=True, index=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed'
    )
    picker_id = fields.Many2one(
        'res.users', string='Picker',
        default=lambda self: self._default_picker_id(),
        help='The user to which the pickings are assigned'
    )
    notes = fields.Text('Notes', help='free form remarks')
    batch_picking_ids = fields.Many2many('stock.picking')
    new_picking_ids = fields.Many2many('stock.picking', string="New pickings")
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        new_ids = self._context.get('active_ids', [])
        moves = self.env['stock.move'].browse(new_ids).mapped('picking_id')
        defaults['new_picking_ids'] = [(6, 0, moves.ids)]
        return defaults

    @api.onchange('batch_id')
    def change_batch_id(self):

        if not self.batch_id:
            self.picking_type_id = False
            self.batch_picking_ids = []
            self.date = False
            self.notes = ''
        self.picking_type_id = self.batch_id and self.batch_id.picking_type_id or False
        self.picker_id = self.batch_id.picker_id
        self.date = self.batch_id.date
        self.notes = self.notes

        picking_ids = self.batch_id and self.batch_id.picking_ids and self.batch_id.picking_ids.ids or False

        if picking_ids:
            self.batch_picking_ids = [(6, 0, picking_ids)]
        else:
            self.batch_picking_ids = []



    def _default_picker_id(self):
        """ Return default_picker_id from the main company warehouse
        except if a warehouse_id is specified in context.
        """
        warehouse_id = self.env.context.get('warehouse_id')
        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        else:
            warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ], limit=1)

        return warehouse.default_picker_id

    @api.multi
    def action_create_batch(self):
        """ Create a batch picking  with selected pickings after having checked
        that they are not already in another batch or done/cancel.
        """
        pickings = self.env['stock.picking'].search([
            ('id', 'in', self.env.context['active_ids']),
            ('batch_picking_id', '=', False),
            ('state', 'not in', ('cancel', 'done'))
        ])

        if not pickings:
            raise UserError(_(
                "All selected pickings are already in a batch picking "
                "or are in a wrong state."
            ))

        batch = self.env['stock.batch.picking'].create({
            'name': self.name,
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
        })

        pickings.write({'batch_picking_id': batch.id})

        return batch.get_formview_action()
