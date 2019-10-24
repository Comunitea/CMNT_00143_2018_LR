# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockBatchDeliveryWzd(models.TransientModel):
    """Create a stock.batch.delivery from stock.moves or stock.quant.packages
    """

    _name = 'stock.batch.delivery.wzd'
    _description = 'Asistente para orden de carga'

    state = fields.Char('State')
    batch_delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga')
    batch_delivery_ids = fields.Many2many('stock.batch.delivery', string='Orden de carga')
    date = fields.Date(
        'Fecha', required=True, index=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed'
    )
    picker_id = fields.Many2one(
        'res.users', string='Usuario',
    )
    notes = fields.Text('Notas', help='free form remarks')
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    driver_id = fields.Many2one('res.partner', string='Conductor',
                                      help='Conductor.',
                                      domain="[('route_driver', '=', True)]")
    plate_id = fields.Many2one('delivery.plate', string='Matrícula', help='Matrícula.')
    cancel_delivery = fields.Boolean('Cancelar order de carga')
    move_ids = fields.Many2many('stock.move', string='Movimientos')
    moves_to_pack_ids = fields.Many2many('stock.move', string='Movimientos sin paquete', inverse='set_moves_to_pack_ids', compute='get_child_vals')
    moves_to_batch_ids = fields.Many2many('stock.move', string='Movimientos sin batch', compute='get_child_vals')
    picking_ids = fields.Many2many('stock.picking', string='Pedidos asociados', compute='get_child_vals')
    packages_ids = fields.Many2many('stock.quant.package', string='Paquetes', compute='get_child_vals')
    moves_to_not_include = fields.Many2many('stock.move', string='Movimientos no incluidos')


    def set_moves_to_pack_ids(self):
        return

    @api.multi
    def get_child_vals(self):
        self.ensure_one()
        self.packages_ids = self.move_ids.mapped('result_package_id')
        self.moves_to_pack_ids = self.move_ids.filtered(lambda x: x.state not in ('assigned', 'partially_available') and not x.result_package_id)
        self.picking_ids = self.move_ids.mapped('picking_id')
        self.moves_to_batch_ids = self.move_ids.filtered(lambda x: not x.batch_id)

    def get_new_batch_values(self, picking_type_id):
        return {
            'date': self.date,
            #'notes': self.notes,
            'picker_id': self.picker_id.id,
            'picking_type_id': picking_type_id.id,
            'state': 'assigned'
        }
    @api.multi
    def action_assign_partner_batch(self):

        if len(self.move_ids.mapped('picking_type_id')) > 1:
            raise ValueError(_('No puedes crear un batch de con movimientos de distiont tipo'))
        picking_type_id = self.move_ids.mapped('picking_type_id')
            # self.move_line_ids.mapped('move_id').ids
        fields = picking_type_id.grouped_batch_field_ids
        new_batchs = self.env['stock.batch.picking']
        if not fields:
            new_batchs = self.env['stock.batch.picking'].create(self.get_wzd_values())
            self.move_ids.write({'draft_batch_picking_id': new_batchs.id})
        else:
            for move in self.move_ids:
                domain = move.get_batch_domain()
                batch = self.env['stock.batch.picking'].search(domain, order='id asc', limit=1)
                if batch:
                    move.draft_batch_picking_id = batch
                else:
                    vals = self.get_new_batch_values(picking_type_id)
                    vals.update(move.get_batch_vals())
                    batch = self.env['stock.batch.picking'].create(vals)
                    move.draft_batch_picking_id = batch
                    new_batchs += batch
            for batch in new_batchs:
                note = 'Notas de los albaranes asociados'
                for pick in batch.draft_move_lines.mapped('picking_id'):
                    if pick.note:
                        note = '{}\n{}\n{}'.format(note, pick.name, pick.note)
                    else:
                        note = '{}\n{}'.format(note, pick.name)

        return self.autorefresh()

    @api.multi
    def action_assign_route(self):

        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'carrier_id': self.carrier_id.id}
        self.with_context(ctx).packages_ids.write(vals)
        self.with_context(ctx).moves_to_pack_ids.write(vals)
        return self.autorefresh()

    def autorefresh(self):
        action = self.env.ref('stock_move_selection_wzd.batch_delivery_wzd_act_window').read()[0]
        action['res_id'] = self.id
        return action

    @api.multi
    def action_packed_moves(self):
        ctx = self._context.copy()
        ctx.update(force_route_vals=True)

        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'carrier_id': self.carrier_id.id}

        for partner_id in self.moves_to_pack_ids.mapped('partner_id'):

            vals.update(partner_id=partner_id.id)
            virtual_package = self.env['stock.quant.package'].with_context(ctx).create(vals)
            vals.update(result_package_id=virtual_package.id)
            self.with_context(ctx).moves_to_pack_ids.write(vals)

        return self.autorefresh()


    @api.model
    def default_get(self, fields):


        active_ids = self._context.get('active_ids')
        if not active_ids:
            raise ValidationError(_('No hay nada seleccionado'))
        if self._context.get('active_model', 'stock_move') == 'stock.picking':
            domain = [('picking_id', 'in', active_ids), ('state', 'in', ('assigned', 'partially_available'))]
            moves = self.env['stock.move'].search(domain)

            domain = [('picking_id', 'in', active_ids), ('state', 'in', ('waiting', 'confirmed'))]
            moves_to_not_include = self.env['stock.move'].search(domain)
        else:
            moves_to_not_include = self.env['stock.move']
            moves = self.env['stock.move'].browse(active_ids)
        moves |= moves.mapped('result_package_id').mapped('move_line_ids').mapped('move_id')
        not_moves = moves.filtered(lambda x: x.picking_type_id.code != 'outgoing')
        if not moves:
            cancel_delivery = True
        else:
            cancel_delivery = False


        if moves.filtered(lambda x: x.batch_delivery_id) and len(moves.mapped('batch_delivery_id')) > 2:
            raise ValidationError(_('Algunos movimientos ya tienen orden de carga seleccionada'))

        if moves.filtered(lambda x: x.state not in ('partially_available', 'assigned')):
            raise ValidationError(_("Tienes movimientos en estado distinto a 'Reservado'"))

        vals = {'cancel_delivery': cancel_delivery}
        domain=[('state', 'in', ('draft', 'ready'))]
        st_ids = []
        for x in moves.mapped('shipping_type'):
            if x and x not in st_ids:
                st_ids.append(x)
        if len(st_ids) == 1:
            vals.update(default_shipping_type=st_ids[0])
            domain += [('shipping_type', '=', st_ids[0] )]

        if len(moves.mapped('delivery_route_path_id')) == 1:
            vals.update(default_delivery_route_path_id=moves[0].delivery_route_path_id.id)
            domain += [('delivery_route_path_id', '=', moves[0].delivery_route_path_id.id)]
        if len(moves.mapped('carrier_id')) == 1:
            vals.update(default_carrier_id=moves[0].carrier_id.id)
            domain += [('carrier_id', '=', moves[0].carrier_id.id)]

        batch_delivery_id = self.env['stock.batch.delivery'].search(domain, limit=1)

        vals.update(default_move_ids = [(6, 0, moves.ids)])
        if batch_delivery_id:
            vals.update(default_batch_delivery_id=batch_delivery_id.id)
        vals.update(default_date=moves and min(moves.mapped('date_expected')))
        vals.update(default_packages_ids=[(6, 0, moves.mapped('result_package_id').ids)])
        vals.update(default_picking_ids=[(6, 0, moves.mapped('picking_id').ids)])
        vals.update(default_moves_to_pack_ids=[(6, 0, moves.filtered(lambda x: not x.result_package_id).ids)])
        vals.update(default_batch_delivery_ids=[(6, 0, moves.mapped('batch_delivery_id').ids)])
        vals.update(default_moves_to_batch_ids=[(6, 0, moves.filtered(lambda x: not x.batch_id).ids)])
        vals.update(default_moves_to_not_include=[(6, 0, moves_to_not_include.ids)])

        ctx = self._context.copy()
        ctx.update(vals)
        if 'active_domain' in ctx.keys():
            ctx.pop('active_domain')
        defaults = super(StockBatchDeliveryWzd, self.with_context(ctx)).default_get(fields)
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

    def get_new_vals(self):
        return {
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
            #'picking_type_id': self.picking_type_id.id,
            'carrier_id': self.carrier_id.id,
            'delivery_route_path_id': self.delivery_route_path_id.id,
            'shipping_type': self.shipping_type,
            'driver_id': self.driver_id.id,
            'plate_id': self.plate_id.id,
        }

    @api.multi
    def in_batch(self, batch_delivery_id):

        """ Create a batch picking  with selected pickings after having checked
        that they are not already in another batch or done/cancel.
        """
        ## compruebo que


        if any(not x.draft_batch_picking_id for x in self.move_ids):
            raise ValidationError('Tienes movimientos sin albarán de cliente')

        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        ## ESCRIBO LAS CANTIDADES PARA QUE ME HAGA SPLIT
        for move in self.move_ids:
            if move.picking_type_id.allow_unpacked or move.result_package_id:
                for ml in move.move_line_ids:
                    ml.qty_done = ml.product_uom_qty
            else:
                raise ValidationError('Tienes movimientos sin paquete')
                ml.qty_done = 0.0

        self.picking_ids.write({'batch_delivery_id': batch_delivery_id.id})
        self.move_ids.filtered(lambda x: x.quantity_done > 0.00).write({'batch_delivery_id': batch_delivery_id.id})
        self.packages_ids.write({'batch_delivery_id': batch_delivery_id.id})
        return batch_delivery_id.get_formview_action()

    @api.multi
    def action_in_batch(self):
        return self.in_batch(self.batch_delivery_id)

    @api.multi
    def action_create_batch(self):

        delivery_batch_vals = self.get_new_vals()
        batch_delivery_id = self.env['stock.batch.delivery'].create(delivery_batch_vals)
        return self.in_batch(batch_delivery_id)
