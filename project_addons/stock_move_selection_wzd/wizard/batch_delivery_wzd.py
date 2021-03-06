# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError


class SBDWMoveLine(models.TransientModel):
    _name = 'sbdw.move.line'

    wzd_id = fields.Many2one('stock.batch.delivery.wzd')
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
    result_package_ids = fields.Many2many(related='move_id.result_package_ids')
    state = fields.Selection(related='move_id.state')
    batch_picking_id = fields.Many2one(related='move_id.batch_picking_id')

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
    line_ids = fields.One2many('sbdw.move.line', 'wzd_id')
    warning = fields.Char ('Warning')

    def set_moves_to_pack_ids(self):
        return

    @api.multi
    def get_child_vals(self):
        self.ensure_one()
        self.packages_ids = self.move_ids.mapped('result_package_id')
        self.moves_to_pack_ids = self.move_ids.filtered(lambda x: x.state in ('assigned', 'partially_available') and not x.result_package_id)
        self.picking_ids = self.move_ids.mapped('picking_id')
        self.moves_to_batch_ids = self.move_ids.filtered(lambda x: not x.batch_picking_id)

    def get_new_batch_values(self, picking_type_id):
        return {
            'date': self.date,
            'picker_id': self.picker_id.id,
            'picking_type_id': picking_type_id.id,
            'state': 'assigned'
        }

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

    def get_wzd_values(self, pick):

        return {
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
            'picking_type_id': pick.picking_type_id.id,
            'state': 'draft',
            'payment_term_id': pick.payment_term_id and pick.payment_term_id.id or False,
            'carrier_id': self.carrier_id and self.carrier_id.id or False,
            'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id or False,
            'shipping_type': self.shipping_type
        }
    @api.multi
    def action_assign_partner_batch(self):
        move_ids = self.line_ids.filtered(lambda x: x.selected).mapped('move_id')
        moves_to_unlink = self.line_ids.filtered(lambda x: not x.selected).mapped('move_id')
        if len(move_ids.mapped('picking_type_id')) > 1:
            raise ValueError(_('No puedes crear un batch de con movimientos de distinto tipo'))
        code = move_ids.mapped('picking_type_id').mapped('code')
        if len(code) != 1 and code[0] != 'outgoing':
            raise ValueError(_('Solo puedes crear batch de tipo cliente (Albaranes de cliente)'))
        new_batchs = self.env['stock.batch.picking']
        picking_ids = move_ids.mapped('picking_id')
        for picking_id in picking_ids:
            domain = picking_id.get_batch_domain()
            batch = self.env['stock.batch.picking'].search(domain, order='id asc', limit=1)
            if not batch:
                vals = self.get_wzd_values(picking_id)
                vals.update(picking_id.get_batch_vals())
                batch = new_batchs.create(vals)
            moves_to_reassign = moves_to_unlink.filtered(lambda x: x.picking_id == picking_id)
            if moves_to_reassign:
                moves_to_reassign.write({'picking_id': False})
                moves_to_reassign._assign_picking()

            picking_id.batch_picking_id = batch.id
            new_batchs |= batch

        new_batchs.set_notes()
        new_batchs.write({'state': 'assigned'})
        return self.autorefresh()


    @api.multi
    def action_assign_route(self):

        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'carrier_id': self.carrier_id.id}
        self.with_context(ctx).packages_ids.write(vals)
        self.with_context(ctx).move_ids.write(vals)
        self.move_ids.mapped('picking_id').compute_route_fields()
        for batch in self.move_ids.mapped('batch_picking_id').filtered(lambda x: x.picking_type_id.code == 'outgoing'):
            batch.compute_route_fields()
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

        elif self._context.get('active_model', 'stock.move') == 'stock.batch.picking':
            batch_picking_ids = self.env['stock.batch.picking'].browse(active_ids)
            moves = batch_picking_ids.move_lines
            moves_to_not_include = moves.filtered(lambda x: x.state not in ('assigned', 'partially_available'))
            moves = moves - moves_to_not_include

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

        if moves.filtered(lambda x: x.state not in ('partially_available', 'assigned', 'confirmed', 'done')):
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
        picking_ids = moves.mapped('picking_id')
        vals.update(default_date=moves and min(moves.mapped('date_expected')))
        vals.update(default_packages_ids=[(6, 0, moves.mapped('result_package_id').ids)])
        vals.update(default_picking_ids=[(6, 0, picking_ids.ids)])
        vals.update(default_moves_to_pack_ids=[(6, 0, moves.filtered(lambda x: not x.result_package_id).ids)])
        vals.update(default_batch_delivery_ids=[(6, 0, moves.mapped('batch_delivery_id').ids)])
        vals.update(default_moves_to_batch_ids=[(6, 0, moves.filtered(lambda x: not x.batch_picking_id).ids)])
        vals.update(default_moves_to_not_include=[(6, 0, moves_to_not_include.ids)])

        move_vals = self.env['stock.batch.picking'].return_move_vals(moves, moves.mapped('picking_id'), complete=True)
        vals.update(default_line_ids=move_vals)
        if picking_ids.mapped('move_lines') != moves:
            vals.update(default_warning = 'Tienes movimeintos del mismo albarán que no serán incluidos en el grupo')
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
        if any(not x.batch_picking_id for x in self.move_ids):
            raise ValidationError('Tienes movimientos sin albarán de cliente')

        ctx = self._context.copy()
        ctx.update(force_route_vals=True)
        ## ESCRIBO LAS CANTIDADES PARA QUE ME HAGA SPLIT
        for move in self.move_ids:

            for ml in move.move_line_ids:
                ml.qty_done = ml.product_uom_qty

            if not move.picking_type_id.allow_unpacked and any(x.result_package_id == False for x in move.move_line_ids):
                raise ValidationError('Tienes movimientos sin paquete')

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
