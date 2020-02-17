# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import SGA_STATES
from odoo.exceptions import UserError, ValidationError

class StockQuantPackagePackLine(models.Model):
    _name = 'stock.quant.package.pack.line'

    def get_domain(self):
        return [('categ_id', '=', 543)]

    package_id = fields.Many2one('stock.quant.package', 'Paquete')
    product_id = fields.Many2one('product.product', 'Producto de empaquetado', required="1", domain=get_domain)
    qty = fields.Integer('Cantidad')
    packaging_move_id = fields.Many2one('stock.move', string="Movimiento de salida asociado")

    @api.multi
    def action_add_pack(self):
        package_id = self.package_id
        package_id.change_packaging_lines(package_id.id, self.product_id.id, relative = 1)

    @api.multi
    def action_minus_pack(self):
        package_id = self.package_id
        package_id.change_packaging_lines(package_id.id, self.product_id.id, relative=-1)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def compute_picking_ids(self):
        for pack in self:
            pack.picking_ids = pack.move_line_ids.mapped('picking_id')
            pack.move_lines = pack.move_line_ids.mapped('move_id')
            pack.batch_picking_ids = pack.picking_ids.mapped('batch_picking_id')


    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado")
    batch_picking_ids = fields.Many2many('stock.batch.picking', compute='compute_picking_ids', string='Grupos')
    batch_delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga')
    partner_id = fields.Many2one(related='move_line_ids.partner_id', store=True)
    picking_ids = fields.One2many('stock.picking', compute='compute_picking_ids')
    packaging_line_ids = fields.One2many('stock.quant.package.pack.line', 'package_id', 'Empaquetado')
    move_lines = fields.One2many('stock.move', compute='compute_picking_ids')

    @api.constrains('move_lines.partner_id', 'move_line.picking_type_id')
    def check_partner(self):
        for pack in self:
            group_code_ids = pack.move_line_ids.mapped('picking_type_id').mapped('group_code')
            if any(x.code == 'outgoing' for x in group_code_ids):
                if len(pack.move_line_ids.mapped('partner_id'))!=1:
                    raise ValidationError (_('No es posible empaquetar para distintos clientes en las operaciones de salida'))

    def get_packaging_lines(self, vals):
        package_id = vals.get('package_id', False)
        if package_id:
            domain = self.env['stock.quant.package.pack.line'].get_domain()
            packaging_products = self.env['product.product'].search(domain)
            package = self.env['stock.quant.package'].browse(package_id)
            pack_lines = []
            for line in package.packaging_line_ids:
                packaging_products -= line.product_id
                new_pack_line = {'package_id': package_id, 'id': line.id, 'product_id': line.product_id.id, 'name': line.product_id.display_name, 'qty': line.qty}
                pack_lines.append(new_pack_line)
            for product in packaging_products:
                new_pack_line = {'package_id': package_id, 'id': 0, 'product_id': product.id, 'name': product.display_name, 'qty': 0}
                pack_lines.append(new_pack_line)
            return  pack_lines
        return []


    @api.model
    def set_packaging_lines(self, vals):
        package_id = vals.get('package_id', False)
        if package_id:
            package = self.env['stock.quant.package'].browse(package_id)
            product_id = vals.get('product_id', False)
            qty = vals.get('qty', False)
            domain = [('package_id','=', package_id), ('product_id', '=', product_id)]
            line = self.env['stock.quant.package.pack.line'].search(domain)
            if not qty:
                line.unlink()
                qty = {'qty': 0}
            else:
                if line:
                    line.qty = qty
                else:
                    line = self.env['stock.quant.package.pack.line'].create({'package_id': package_id, 'product_id': product_id, 'qty': qty})
                qty = {'qty': line.qty}
            return qty
        return False

    @api.model
    def change_packaging_lines(self, package_id=False, product_id=False, relative = 0, absolute=0):
        if package_id and product_id:
            package_id = self.browse(package_id)
            product_id = self.env['product.product'].browse(product_id)
            line = package_id.packaging_line_ids.filtered(lambda x: x.product_id == product_id)
            if line:
                if relative:
                    qty = max(0, line.qty + relative)
                else:
                    qty = absolute
                if qty > 0: line.qty = qty
                if qty == 0:
                    line.unlink()
            if not line and (absolute > 0 or relative > 0):
                qty = absolute + relative
                if qty > 0:
                    package_id.write({'packaging_line_ids': [(6, 0, {'product_id': product_id.id, 'qty': qty})]})

    @api.onchange('delivery_route_path_id', 'shipping_type', 'carrier_id')
    def onchange_route_fields(self):
        if self._context.get('force_route_fields', False) and (self.batch_picking_id or self.batch_delivery_id):
            raise ValidationError ('No puedes cambiar los datos de envío si el paquete está en un grupo')

    @api.model
    def create(self, vals):
        if vals.get('name') == '*':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.quant.package')
        return super().create(vals)

    @api.multi
    def action_done(self):
        for package in self:
            domain = [('state', 'in', ('partially_available', 'assigned')), ('move_id', '!=', False), ('result_package_id', '=', package.id)]
            todo_moves = self.env['stock.move.line'].search(domain).mapped('move_id')
            for move in todo_moves:
                move.qty_done = move.reserved_availability
            todo_moves._action_done()

    @api.multi
    def add_package_to_batch(self):
        batch_picking_id = self.env['stock.batch.picking'].browse(self._context.get('batch_picking_id'))

        if batch_picking_id.state not in ['draft', 'assigned']:
            raise ValidationError(_('You can not add packages to a batch picking done or canceled.'))

        move_domain = [('result_package_id', '=', self.id)]
        moves = self.env['stock.move.line'].search(move_domain).mapped('move_id')

        if not moves:
            raise ValidationError("This pack is empty!")

        for move in moves:
            if batch_picking_id.shipping_type == 'pasaran':
                move.write({'origin': '{} / {}'.format(batch_picking_id.date, batch_picking_id.shipping_type)})
            elif batch_picking_id.shipping_type == 'route':
                move.write({'origin': '{} / {}'.format(batch_picking_id.date, batch_picking_id.delivery_route_id.name)})
            elif batch_picking_id.shipping_type == 'agency':
                move.write({'origin': '{} / {}'.format(batch_picking_id.date, batch_picking_id.carrier_id.name)})

        ctx = self._context.copy()
        ctx.update(default_shipping_type=self.shipping_type)
        for move in moves:
            move.with_context(ctx).action_force_assign_picking()
        self.write({'batch_picking_id': self._context.get('batch_picking_id')})
        return

    @api.multi
    def delete_package_from_batch(self, package_id):
        raise ValueError (_('No implementado'))
        ctx = self._context.copy()
        ctx.update(batch_picking_id=ctx.get('batch_picking_id'))

        batch_picking_id = self.env['stock.batch.picking'].browse(ctx.get('batch_picking_id'))

        if batch_picking_id.state not in ['draft', 'assigned']:
            raise ValidationError(_('You can not add packages to a batch picking done or canceled.'))
        else:
            move_lines = self.env['stock.quant.package'].browse(package_id).move_line_ids
            picking_ids = move_lines.mapped('move_id').mapped('picking_id')
            for picking_id in picking_ids:
                self.env['stock.picking'].browse(picking_id.id).write({
                    'batch_picking_id': False
                })
            self.env['stock.quant.package'].browse(package_id).write({
                'batch_picking_id': False
            })
            for line in move_lines:
                self.env['stock.move.line'].browse(line.id).write({
                    'picking_id': False
                })
                self.env['stock.move'].browse(line.move_id.id).write({
                    'picking_id': False
                })

    def action_view_moves_line(self):

        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]

        action['domain'] = [('id', 'in', self.move_line_ids.mapped('move_id').ids)]
        action['views'] = [(tree and tree.id or False, 'tree'), (False, 'form'),
                           (kanban and kanban.id or False, 'kanban')]
        action['context'] = {}
        return action

    #
    # @api.multi
    # def write(self, vals):
    #     return super().write(vals)
    #
    #
    # def update_package_shipping_values(self, shipping_type=False, delivery_route_path_id=False, carrier_id=False):
    #
    #     vals = {}
    #     if shipping_type:
    #         vals.update(shipping_type=shipping_type)
    #     if delivery_route_path_id:
    #         vals.update(delivery_route_path_id=delivery_route_path_id)
    #     if carrier_id:
    #         vals.update(carrier_id=carrier_id)
    #     if vals:
    #         vals.update(picking_id=False, bacht_picking_id=False, batch_delivery_id=False)
    #
    #     for pack in self:
    #         if any(move.state in ('done', 'cancel') for move in pack.move_line_ids):
    #             raise exceptions.ValidationError('No puedes cambiar en un movimiento hecho o cancelado')
    #
    #         if pack.batch_delivery_id :
    #             raise exceptions.ValidationError('No puedes cambiar en un paquete que ya está en una orden de carga')
    #
    #         moves = pack.move_line_ids.mapped('move_id')
    #         moves.write(vals)
    #         moves.assign_picking()

    @api.multi
    def picking_pack_lines(self, batch_picking_id=False):
        lines = self.mapped('packaging_line_ids').filtered(lambda x: not x.packaging_move_id)
        if not lines:
            return False
        if not batch_picking_id:
            batch_picking_id = self.batch_picking_id
        if not batch_picking_id:
            raise ValueError(_('Debes asignar primero a un albarán de cliente'))

        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('group_code.code', '=', 'packaging')], limit=1)
        # crea un stock picking para las líneas de los m0vimientos
        move_ids = self.env['stock.move']
        lines = self.mapped('packaging_line_ids')
        partner_id = self.mapped('move_line_ids').mapped('partner_id')
        #move_ids = self.mapped('move_line_ids').mapped('move_id')

        if len(partner_id)!=1:
            raise ValueError(_('No puedes crearlo de varios clientes al mismo tiempos'))
        moves = {}
        for line in lines:
            if line.product_id in moves:
                moves[line.product_id].product_qty += line.qty
            else:
                val = {
                    'name': line.product_id.display_name,
                    'partner_id': partner_id.id,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.qty,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                    'picking_type_id': picking_type_id.id,
                    'shipping_type': batch_picking_id.shipping_type,
                    'delivery_route_path_id': batch_picking_id.delivery_route_path_id and batch_picking_id.delivery_route_path_id.id or False,
                    'carrier_id': batch_picking_id.carrier_id and batch_picking_id.carrier_id.id or False,
                }

                new_move = move_ids.create(val)
                line.write({'packaging_move_id': new_move.id})
                new_move._action_confirm()
                new_move._action_assign()
                new_move._assign_picking()
                moves[line.product_id] = new_move
                move_ids |= new_move


        picking_id = move_ids.mapped('picking_id')

        new_batch_vals = {
            'name': picking_id.name,
            'partner_id': partner_id.id,
            'orig_batch_picking_id': batch_picking_id.id,
            #'location_id': picking_id.location_id.id,
            #'location_dest_id': picking_id.location_dest_id.id,
            'picking_type_id': picking_type_id.id,
            'picking_ids': [(6,0, [picking_id.id])]

        }
        batch = self.env['stock.batch.picking'].create(new_batch_vals)
        batch_picking_id.pack_lines_picking_id = batch
        if batch_picking_id.state == 'done':
            batch.action_transfer()
        return batch





    @api.multi
    def action_cancel_delivery_batch_assigment(self):
        for package in self:
            if package.batch_delivery_id:
                if package.batch_delivery_id.state == 'done':
                    raise ValidationError(_('No es posible sacar el paquete {} de la orden de carga {}. Ya está realizada'.format(package.name, package.batch_delivery_id.name)))
                if package.batch_delivery_id.state == 'ready':
                    raise ValidationError(_('Debes poner la orden de carga {} en estado borrador para poder sacar el paquete'.format(package.batch_delivery_id.name)))
            package.batch_delivery_id = False

















