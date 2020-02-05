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

class SBPWMoveLine(models.TransientModel):
    _name = 'sbpw.move.line'

    wzd_id = fields.Many2one('stock.batch.picking.wzd')
    selected = fields.Boolean(string="Seleccionado")
    move_id = fields.Many2one('stock.move')
    product_id = fields.Many2one(related='move_id.product_id')
    partner_id = fields.Many2one(related='move_id.partner_id')
    orig_picking_id = fields.Many2one(related='move_id.orig_picking_id')
    product_uom_qty = fields.Many2one(related='move_id.product_uom_qty')
    quantity_done = fields.Float(related='move_id.quantity_done')
    reserved_availability = fields.Float(related='move_id.reserved_availability')
    product_uom_qty = fields.Float(related='move_id.product_uom_qty')
    origin = fields.Char(related='move_id.origin')
    info_route_str = fields.Char(related='move_id.info_route_str')
    result_package_id = fields.Many2one(related='move_id.result_package_id')
    state = fields.Selection(related='move_id.state')
    batch_picking_id = fields.Many2one(related='move_id.batch_picking_id')

class SBPWPickLine(models.TransientModel):
    _name = 'sbpw.pick.line'

    wzd_id = fields.Many2one('stock.batch.picking.wzd')
    picking_id = fields.Many2one('stock.picking')
    batch_picking_id = fields.Many2one(related='picking_id.batch_picking_id')
    partner_id = fields.Many2one(related='picking_id.partner_id')
    info_route_str = fields.Char(related='picking_id.info_route_str')
    name = fields.Char(related='picking_id.name')
    origin = fields.Char(related='picking_id.origin')
    count_move_lines = fields.Integer(related='picking_id.count_move_lines')
    state = fields.Selection(related='picking_id.state')


    def button_unlink_from_batch(self):

        for line in self:
            moves = self.wzd_id.move_ids
            moves.filtered(lambda x: x.move_id.picking_id.id == line.picking_id.id).unlink()

        action = self.wzd_id.get_formview_action()
        action['target'] = 'new'
        # return action

        action['res_id'] = self.wzd_id.id
        self.unlink()
        return action

class StockBatchPickingWzd(models.TransientModel):
    """Create a stock.batch.picking from stock.picking
    """

    _name = 'stock.batch.picking.wzd'
    _description = 'Asistente para agrupar albaranes'

    @api.model
    def _get_batch_picking_domain(self):
        print ("BUSCANDO DOMINIO")
        domain = [('state', '=', 'draft'),
                  ('picking_type_id', '=', self.picking_type_id.id)]
        for field in self.picking_type_id.grouped_batch_field_ids:
            if self[field.name]:
                if field.ttype == 'many2one':
                    domain += [(field.name, '=', self[field.name].id)]
                else:
                    domain += [(field.name, '=', self[field.name])]

        batch = self.env['stock.batch.picking'].search(domain, order='id asc')
        print ('Dominio: {}\n {}'.format(domain, [x.name for x in batch]))
        return domain

    batch_picking_id = fields.Many2one('stock.batch.picking', 'Grupo')
    batch_picking_ids = fields.Many2many('stock.batch.picking')

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
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta de entrega")
    carrier_id = fields.Many2one("delivery.carrier", string="Forma de envío")
    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago')
    move_ids = fields.One2many('sbpw.move.line', 'wzd_id')
    picking_ids = fields.One2many('sbpw.pick.line', 'wzd_id')
    warning = fields.Char ('Warning')

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
        if picking_type_id and len(picking_type_id) != 1:
            raise UserError(_('No se pueden agrupar alabranes de distinto tipo'))
        g_fields = picking_type_id.grouped_batch_field_ids.mapped('name')
        delivery_route_path_id = moves.mapped('delivery_route_path_id')
        if len(delivery_route_path_id) > 1:
            if 'delivery_route_path_id' in g_fields:
                raise UserError (_('No se puede agrupar este tipo de albarnes por distintas valores para el campo ruta: {}'.format([x.name for x in delivery_route_path_id])))
            delivery_route_path_id = False


        carrier_id = moves.mapped('carrier_id')
        if len(carrier_id) >1 :
            if 'carrier_id' in g_fields:
                raise UserError (_('No se puede agrupar este tipo de albaranes por distintas valores para el campo entrega: {}'.format([x.name for x in carrier_id])))
            carrier_id = False

        payment_term_id = moves.mapped('payment_term_id')
        if len(payment_term_id) > 1:
            if 'payment_term_id' in g_fields:
                raise UserError(_(
                    'No se puede agrupar este tipo de albaranes por distintas valores para el campo plazos de pago: {}'.format(
                        [x.name for x in payment_term_id])))
            payment_term_id = False

        batch_picking_id = moves.mapped('batch_picking_id')
        if len(batch_picking_id) > 1:
            raise UserError(_('Ya tienes seleccionados varios batchs: {}'.format(batch_picking_id.mapped('name'))))


        picker_id = batch_picking_id and batch_picking_id.picker_id or False
        note = 'Notas de los albaranes asociados'
        for pick in picking_ids:
            if pick.note:
                note = '{}\n{}\n{}'.format(note, pick.name, pick.note)
            else:
                note = '{}\n{}'.format(note, pick.name)

        dates = moves.mapped('picking_id').mapped('scheduled_date')
        dates.append(fields.Datetime.now())
        date = min(dates)
        if date < fields.Date.today():
            date = fields.Date.today()

        move_vals = self.env['stock.batch.picking'].return_move_vals(moves, picking_ids, complete=True)
        pick_vals = self.env['stock.batch.picking'].return_pick_vals(picking_ids, complete=True)
        vals = {
            'date': date,
            'picking_type_id': picking_type_id and picking_type_id.id or False,
            'batch_picking_id': batch_picking_id and batch_picking_id.id or False,
            'picker_id': picker_id and picker_id.id  or False,
            'notes': note,
            'payment_term_id': payment_term_id and payment_term_id.id or False,
            'carrier_id': carrier_id and carrier_id.id or False,
            'move_ids': move_vals,
            'picking_ids': pick_vals,
            'warning': 'Avisos',
            'delivery_route_path_id': delivery_route_path_id and delivery_route_path_id.id  or False,
        }

        if picking_ids.mapped('move_lines') != moves:
            vals.update(warning='Tienes movimeintos del mismo albarán que no serán incluidos en el grupo')

        shipping_type = []
        for move in moves:
            if move.shipping_type not in shipping_type:
                shipping_type.append(move.shipping_type)
        if len(shipping_type) == 1:
            vals.update(shipping_type=shipping_type[0])

        batch_picking_ids = self._get_batch_picking_ids(vals)
        if batch_picking_ids:
            vals.update(batch_picking_ids=[(6,0,batch_picking_ids.ids)])
            if not batch_picking_id:
                 vals.update(batch_picking_id=batch_picking_ids[0].id)
        return vals

    def _get_batch_picking_ids(self, vals):
        domain = [('state', '=', 'draft'),
                  ('picking_type_id', '=', vals['picking_type_id'])]
        for field in self.picking_type_id.grouped_batch_field_ids:
            if self[field.name] and vals[field.name]:
                domain += [(field.name, '=', vals[field.name])]
        batch = self.env['stock.batch.picking'].search(domain, order='id asc')
        return batch

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        if self._context.get('reload'):
            return defaults
        model = self._context.get('model', self._context.get('active_model', 'stock.move'))
        if model in ['stock.move', 'stock.picking']:
            new_ids = self._context.get('active_ids', [])
            vals = self.get_vals(model, ids=new_ids)
            if self._context.get('get_vals', True):
                defaults.update(vals)
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
            'state': 'draft',
            'payment_term_id': self.payment_term_id and self.payment_term_id.id or False,
            'carrier_id': self.carrier_id and self.carrier_id.id or False,
            'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id or False,
            'shipping_type': self.shipping_type
        }

    @api.multi
    def action_apply_info_envio(self):

        vals = {'date_expected': self.date}
        if self.shipping_type:
            vals.update(shipping_type=self.shipping_type)
        if self.delivery_route_path_id:
            vals.update(delivery_route_path_id=self.delivery_route_path_id.id)
        if self.carrier_id:
            vals.update(carrier_id=self.carrier_id.id)

        move_ids = self.move_ids.filtered(lambda x: x.selected).mapped('move_id')
        move_ids.assign_info_envio(vals)
        return self.reload_wzd()

    @api.multi
    def action_create_batch(self):
        if len(self.mapped('picking_type_id'))>1:
            raise ValueError(_('No puedes crear un batch de con movimientos de distiont tipo'))
        new_batchs = self.env['stock.batch.picking']
        move_ids = self.move_ids.filtered(lambda x: x.selected).mapped('move_id')
        picking_ids = move_ids.mapped('picking_id')
        for pick in picking_ids:
            moves = move_ids.filtered(lambda x: x.picking_id == pick)
            if not self.batch_picking_id:
                domain = pick.get_batch_domain()
                if new_batchs:
                    domain += [('id', 'in', new_batchs.ids)]
                batch = self.env['stock.batch.picking'].search(domain,  order='id asc', limit=1)
            else:
                batch = self.batch_picking_id
            if not batch:
                vals = self.get_wzd_values()
                vals.update(pick.get_batch_vals())
                batch = self.env['stock.batch.picking'].create(vals)

            moves.assign_batch_picking_id(batch)
            new_batchs |= batch

        for batch in new_batchs:
            note = 'Notas de los albaranes asociados'
            for pick in batch.picking_ids:
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
            ## miro si el picking tiene el mismo batch o está vacío
            picking_ids = self.move_ids.filtered(lambda x:x.selected).mapped('picking_id')
            moves_to_assign = self.move_ids.mapped('move_id')

            for picking_id in picking_ids:
                pick_moves_to_unlink = picking_id.move_lines - moves_to_assign.filtered(lambda x: x.picking_id == picking_id)
                if pick_moves_to_unlink:
                    pick_moves_to_unlink.write({'picking_id': False})
                    picking_id.batch_picking_id

            moves_to_link = self.move_ids.filtered(lambda x:x.selected).mapped('move_id')
            domain = [('batch_picking_id', '=', self.batch_picking_id.id), ('id', 'not in', moves_to_link.ids)]
            moves_to_unlink = self.env['stock.move'].search(domain)
            moves_to_unlink.write({'batch_picking_id': False})
            moves_to_link.write({'batch_picking_id': self.batch_picking_id.id})
            self.batch_picking_id.compute_route_fields()
        else:
            return self.reload_wzd()

    @api.multi
    def reload_wzd(self):
        self.ensure_one()
        action = self.get_formview_action()
        action['target'] = 'new'
        action['res_id'] = self._context.get('active_id', self.id)
        return action

    @api.multi
    def write(self, vals):
        return super().write(vals)
