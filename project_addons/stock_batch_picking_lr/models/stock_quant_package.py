# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo import exceptions 

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    batch_picking_id = fields.Many2one('stock.batch.picking', 'Stock Batch')
    in_batch = fields.Boolean(compute="_check_if_in_batch", default=False)

    @api.multi
    def _check_if_in_batch(self):
        for package in self:
            ctx = self._context.copy()
            batch_picking_id = ctx.get('batch_picking_id')
            stock_batch = self.browse(batch_picking_id)
            if stock_batch and package.mapped('move_line_ids').mapped('picking_id') and stock_batch.id == package.mapped('move_line_ids').mapped('picking_id').mapped('batch_picking_id').id:
                package.in_batch = True
            else:
                package.in_batch = False
    
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
                move.write({'origin':'{} / {}'.format(batch_picking_id.date, batch_picking_id.shipping_type)})
            elif batch_picking_id.shipping_type == 'route':
                move.write({'origin':'{} / {}'.format(batch_picking_id.date, batch_picking_id.delivery_route_id.name)})
            elif batch_picking_id.shipping_type == 'agency':
                move.write({'origin':'{} / {}'.format(batch_picking_id.date, batch_picking_id.carrier_id.name)})

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
                    'batch_picking_id' : False
                })
            self.env['stock.quant.package'].browse(package_id).write({
                'batch_picking_id' : False
            })
            for line in move_lines:
                self.env['stock.move.line'].browse(line.id).write({
                    'picking_id': False
                })
                self.env['stock.move'].browse(line.move_id.id).write({
                    'picking_id': False
                })  
