# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class StockBatchPickingWzd(models.TransientModel):
    """Create a stock.batch.picking from stock.picking
    """

    _name = 'stock.batch.picking.wzd'
    _description = 'Asistente para agrupar albaranes'


    batch_picking_id = fields.Many2one('stock.batch.picking', 'Grupo')
    date = fields.Date(
        'Fecha prevista', required=True, index=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed'
    )
    picker_id = fields.Many2one(
        'res.users', string='Usuario',
        default=lambda self: self._default_picker_id(),
        help='The user to which the pickings are assigned'

    )
    notes = fields.Text('Notes', help='free form remarks')
    batch_picking_ids = fields.Many2many('stock.picking', string="Grupos")
    new_picking_ids = fields.Many2many('stock.picking', string="Nuevos albaranes")
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación')
    moves_to_remove = fields.Many2many('stock.move', string="Movimientos para eliminar")
    moves_to_sga = fields.Many2many('stock.move', string="Para enviar a SGA")
    moves_not_sga = fields.Many2many('stock.move', string="Sin enviar a SGA")
    move_ids = fields.Many2many('stock.move', string="Movimientos")
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de entrega")
    carrier_id = fields.Many2one("delivery.carrier", string="Forma de envío")
    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')

    def create_from(self, model='stock.move', ids=[]):
        vals = self.get_vals(model, ids=ids)
        wzd_id = self.create(vals)
        return wzd_id

    def get_vals(self, model='stock.move', ids = []):

        if model=='stock.move':
            moves = self.env[model].browse(ids)
            picking_ids = moves.mapped('picking_id')
        elif model=='stock.picking':
            picking_ids = self.env[model].browse(ids)
            moves = self.mapped('move_lines')
        else:
            return {}
        picking_type_id = moves.mapped('picking_type_id')
        if len(picking_type_id)>1:
            raise UserError(_('No se pueden agrupar alabranes de distinto tipo'))

        batch_picking = moves.mapped('batch_picking_id')
        batch_picking_id = len(batch_picking) == 1 and batch_picking.id
        picker_id = batch_picking and batch_picking.picker_id and batch_picking.picker_id.id

        note = 'Notas de los albaranes asociados'
        for pick in picking_ids:
            if pick.note:
                note = '{}\n{}\n{}'.format(note, pick.name, pick.note)
            else:
                note = '{}\n{}'.format(note, pick.name)

        if batch_picking_id:
            new_picking_ids = picking_ids
            batch_picking_ids = self.env['stock.batch.picking']
        else:
            new_picking_ids = picking_ids.filtered(lambda x: x.batch_picking_id.id != batch_picking_id)
            batch_picking_ids = picking_ids.filtered(lambda x: x.batch_picking_id.id == batch_picking_id)

        if picking_type_id.sga_integrated:
            moves_to_sga = moves.filtered(lambda x: x.sga_state != 'NI')
            moves_not_sga = moves.filtered(lambda x: x.sga_state == 'NI')
        else:
            moves_to_sga = moves_not_sga = self.env['stock.move']

        vals = {
            'date':min(picking_ids.mapped('scheduled_date')),
            'picking_type_id': picking_type_id and picking_type_id.id or False,
            'batch_picking_id': batch_picking and batch_picking_id or False,
            'picker_id': picker_id and picker_id.id or False,
            'notes': note,
            'new_picking_ids': [(6,0,new_picking_ids.ids)],
            'batch_picking_ids': [(6,0,batch_picking_ids.ids)],
            'move_ids': [(6, 0, moves.ids)],
            'moves_to_sga': [(6, 0, moves_to_sga.ids)],
            'moves_not_sga': [(6, 0, moves_not_sga.ids)]
            }
        return vals

    @api.model
    def default_get(self, fields):

        if self._context.get('active_model', False) == 'stock.picking.type':
            return super().default_get(fields)


        defaults = super().default_get(fields)
        new_ids = self._context.get('active_ids', [])
        if new_ids:
            ctx = self._context.copy()
            ctx.update(active_model = 'stock.picking.type')
            self = self.with_context(ctx)
            model = self._context.get('model', self._context.get('active_model', 'stock.move'))
            wzd_id = self.create_from(model, new_ids)
            action = self.env.ref('stock_move_selection_wzd.batch_picking_wzd_act_window').read()[0]
            action['res_id'] = wzd_id.id
            print (action)

            return action

            defaults.update(vals)
            print (defaults)
        return defaults


    @api.onchange('batch_picking_id')
    def change_batch_id(self):
        if not self.batch_picking_id:
            self.picking_type_id = False
            self.batch_picking_ids = []
            self.date = False
            self.notes = ''
        self.picking_type_id = self.batch_picking_id and self.batch_picking_id.picking_type_id or False
        self.picker_id = self.batch_picking_id.picker_id
        self.date = self.batch_picking_id.date
        self.notes = self.notes

        picking_ids = self.batch_picking_id and self.batch_picking_id.picking_ids and self.batch_picking_id.picking_ids.ids or False

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
    def action_create_batch_split(self):
        """ Create a batch picking  with selected pickings after having checked
        that they are not already in another batch or done/cancel.
        """

        if self.moves_to_remove:
            vals = {'picking_id': False}
            self.moves_to_remove.mapped('move_line_ids').write(vals)
            self.moves_to_remove.write(vals)
            self.moves_to_remove.mapped('result_package_id').write(vals)

        if self.batch_picking_id:
            self.new_picking_ids.write({'batch_picking_id': self.batch.id})
            return self.batch_picking_id.get_formview_action()

        batch = self.env['stock.batch.picking'].create({
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
            'picking_type_id': self.picking_type_id.id,
            #'carrier_id': self.carrier_id.id,
            #'delivery_route_path_id': self.delivery_route_path_id.id,
            #'shipping_type': self.shipping_type
        })

        self.new_picking_ids.write({'batch_picking_id': batch.id})
        if self.moves_to_remove:
            self.moves_to_remove.action_force_assign_picking()
        return batch.get_formview_action()

    @api.multi
    def action_create_batch(self):
        batch_picking_id = self.env['stock.batch.picking'].create({
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
            'picking_type_id': self.picking_type_id.id,
            #'carrier_id': self.carrier_id.id,
            #'delivery_route_path_id': self.delivery_route_path_id.id,
            #'shipping_type': self.shipping_type
        })
        self.new_picking_ids.write({'batch_picking_id': batch_picking_id.id})
        return batch_picking_id.get_formview_action()