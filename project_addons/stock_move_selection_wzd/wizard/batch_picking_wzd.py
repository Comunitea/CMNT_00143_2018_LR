# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class OpenBatchWzd(models.TransientModel):
    _name = 'open.batch.wzd'

    @api.multi
    def continue_to_wzd(self):
        domain = [('id', 'in', self._context.get('active_ids'))]
        return self.env['stock.move'].search(domain).action_add_to_batch_picking()

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
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación')
    move_ids = fields.Many2many('stock.move', string="Movimientos")
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de entrega")
    carrier_id = fields.Many2one("delivery.carrier", string="Forma de envío")
    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    picking_ids = fields.Many2many('stock.picking', string="Albaranes")
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago')

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
            moves = picking_ids.mapped('move_lines')
        else:
            return {}

        picking_type_id = moves.mapped('picking_type_id')
        if len(picking_type_id)>1:
            raise UserError(_('No se pueden agrupar alabranes de distinto tipo'))

        delivery_route_path_id = moves.mapped('delivery_route_path_id')
        if len(delivery_route_path_id) == 1:
            delivery_route_path_id = False

        payment_term_id = moves.mapped('payment_term_id')
        if len(payment_term_id)>1:
            if picking_type_id.code == 'outgoing':
                raise UserError(_('No se pueden agrupar albaranes con formas de pago distintas'))
            payment_term_id = self.env['account.payment.term']

        batch_picking = moves.mapped('draft_batch_picking_id')
        if len(batch_picking)>1:
            raise UserError(_('Ya tienes seleccionados varios batchs: {}'.format(batch_picking.mapped('name'))))
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
            moves_to_sga = moves.filtered(lambda x: x.sga_state != 'no_integrated')
            moves_not_sga = moves.filtered(lambda x: x.sga_state == 'no_integrated')
        else:
            moves_to_sga = moves_not_sga = self.env['stock.move']

        date = min(moves.mapped('picking_id').mapped('scheduled_date'))
        if date < fields.Date.today():
            date = fields.Date.today()

        vals = {
            'date':date,
            'picking_type_id': picking_type_id and picking_type_id.id or False,
            'batch_picking_id': batch_picking and batch_picking_id or False,
            'picker_id': picker_id and picker_id.id or False,
            'notes': note,
            'payment_term_id': payment_term_id and payment_term_id.id or False,
            'carrier_id': self.carrier_id and self.carrier_id.id or False,
            'move_ids': [(6, 0, moves.ids)],

            'delivery_route_path_id': delivery_route_path_id and delivery_route_path_id.id or False,
            }
        shipping_type = []
        for move in moves:

            if move.shipping_type not in shipping_type:
                shipping_type.append(move.shipping_type)
        if len(shipping_type) == 1:
            vals.update(shipping_type=shipping_type[0])

        if model == 'stock.picking':
            vals.update(picking_ids=[(6,0,picking_ids.ids)])
        return vals

    @api.model
    def default_get(self, fields):

        defaults = super().default_get(fields)
        model = self._context.get('model', self._context.get('active_model', 'stock.move'))
        new_ids = self._context.get('active_ids', [])
        defaults.update(self.get_vals(model, ids=new_ids))
        return defaults

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
            'picker_id': self.picker_id and self.picker_id.id or False,
            'picking_type_id': self.picking_type_id.id,
            'payment_term_id': self.payment_term_id and self.payment_term_id.id or False,
            'carrier_id': self.carrier_id and self.carrier_id.id or False,
            'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id or False,
            'shipping_type': self.shipping_type
        })

        self.new_picking_ids.write({'batch_picking_id': batch.id})
        if self.moves_to_remove:
            self.moves_to_remove.action_force_assign_picking()
        return batch.get_formview_action()

    def get_wzd_values(self):
        return {
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
            'picking_type_id': self.picking_type_id.id,
            'state': 'assigned',
            'payment_term_id': self.payment_term_id and self.payment_term_id.id or False,
            'carrier_id': self.carrier_id and self.carrier_id.id or False,
            'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id or False,
            'shipping_type': self.shipping_type
        }


    @api.multi
    def action_create_batch(self):
        if len(self.mapped('picking_type_id'))>1:
            raise ValueError(_('No puedes crear un batch de con movimientos de distiont tipo'))

        #self.move_line_ids.mapped('move_id').ids
        fields = self.picking_type_id.grouped_batch_field_ids
        new_batchs = self.env['stock.batch.picking']
        if not fields:
            new_batchs = self.env['stock.batch.picking'].create(self.get_wzd_values())
            self.move_ids.write({'draft_batch_picking_id': new_batchs.id})
        else:
            for move in self.move_ids:
                domain = move.get_batch_domain()
                batch = self.env['stock.batch.picking'].search(domain,  order='id asc', limit=1)
                if batch:
                    move.draft_batch_picking_id = batch
                else:
                    vals = self.get_wzd_values()
                    vals.update(move.get_batch_vals())
                    batch = self.env['stock.batch.picking'].create(vals)
                    move.draft_batch_picking_id = batch
                    new_batchs += batch
        for batch in new_batchs:
            note = 'Notas de los albaranes asociados'
            for pick in batch.draft_move_lines.mapped('picking_id'):
                pick.draft_batch_picking_id = batch.id
                if pick.note:
                    note = '{}\n{}\n{}'.format(note, pick.name, pick.note)
                else:
                    note = '{}\n{}'.format(note, pick.name)
        if self._context.get('send', True):
            new_batchs.send_to_sga()
        action = self.env.ref('stock_batch_picking.action_stock_batch_picking_tree').read()[0]
        action['domain'] = [('id', 'in', new_batchs.ids)]
        return action



    @api.multi
    def unlink(self):
        if any(x.state == 'done' for x in self):
            raise ValueError(_('No puedes suprimir un batch realizado))'))
        return super().unlink()

    @api.multi
    def action_assign_batch(self):
        if self.batch_picking_id:
            self.move_ids.write({'draft_batch_picking_id': self.batch_picking_id.id})
            self.move_ids.mapped('picking_id').write({'draft_batch_picking_id': self.batch_picking_id.id})
        return self.batch_picking_id.get_formview_action()


    @api.multi
    def write(self, vals):
        return super().write(vals)
