# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import SGA_STATES
from odoo import exceptions

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def _get_picking_ids(self):
        for pack in self:
            pack.picking_ids = pack.move_line_ids.mapped('picking_id')

    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")
    batch_picking_id = fields.Many2one('stock.batch.picking', 'Grupo')
    batch_delivery_id = fields.Many2one('stock.batch.delivery', 'Orden de carga')
    partner_id = fields.Many2one(related='move_line_ids.partner_id', store=True)
    picking_ids = fields.One2many(compute=_get_picking_ids)

    @api.onchange('delivery_route_path_id', 'shipping_type', 'carrier_id')
    def onchange_route_fields(self):
        if self.context.get('force_route_fields', False) and (self.batch_picking_id or self.batch_delivery_id):
            raise exceptions.ValidationError ('No puedes cambiar los datos de envío si el paquete está en un grupo')

    @api.onchange('batch_delivery_id')
    def onchange_dp_id(self):
        print(self._context)

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
            raise exceptions.ValidationError(_('You can not add packages to a batch picking done or canceled.'))

        move_domain = [('result_package_id', '=', self.id)]
        moves = self.env['stock.move.line'].search(move_domain).mapped('move_id')

        if not moves:
            raise exceptions.ValidationError("This pack is empty!")

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

        ctx = self._context.copy()
        ctx.update(batch_picking_id=ctx.get('batch_picking_id'))

        batch_picking_id = self.env['stock.batch.picking'].browse(ctx.get('batch_picking_id'))

        if batch_picking_id.state not in ['draft', 'assigned']:
            raise exceptions.ValidationError(_('You can not add packages to a batch picking done or canceled.'))
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


    @api.multi
    def write(self, vals):
        if 'batch_delivery_id' in vals and len(vals.keys())==1:
            print (self._context)
            print(vals)

        return super().write(vals)


    def update_package_shipping_values(self, shipping_type=False, delivery_route_path_id=False, carrier_id=False):

        vals = {}
        if shipping_type:
            vals.update(shipping_type=shipping_type)
        if delivery_route_path_id:
            vals.update(delivery_route_path_id=delivery_route_path_id)
        if carrier_id:
            vals.update(carrier_id=carrier_id)
        if vals:
            vals.update(picking_id=False, bacht_picking_id=False, batch_delivery_id=False)

        for pack in self:
            if any(move.state in ('done', 'cancel') for move in pack.move_line_ids):
                raise ValueError('No puedes cambiar en un movimiento hecho o cancelado')


            moves = pack.move_line_ids.mapped('move_id')
            moves.write(vals)
            moves.assign_picking()








