# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from pprint import pprint
from odoo import exceptions 

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    stock_batch_id = fields.Many2one('stock.batch.picking', 'Stock Batch')
    in_batch = fields.Boolean(compute="_check_if_in_batch", default=False)

    @api.multi
    def _check_if_in_batch(self):
        for package in self:
            ctx = self._context.copy()
            stock_batch_id = ctx.get('stock_batch_id')
            stock_batch = self.browse(stock_batch_id)
            if stock_batch and package.mapped('move_line_ids').mapped('picking_id') and stock_batch.id == package.mapped('move_line_ids').mapped('picking_id').mapped('batch_picking_id').id:
                package.in_batch = True
            else:
                package.in_batch = False
    
    @api.model
    def add_package_to_batch(self, package_id):
        ctx = self._context.copy()
        ctx.update(batch_picking_id=ctx.get('stock_batch_id'))

        batch_picking_id = self.env['stock.batch.picking'].browse(ctx.get('stock_batch_id'))

        moves = self.env['stock.quant.package'].browse(package_id).mapped('move_line_ids').mapped('move_id')

        if moves:
            for move in moves:
                move.write({'origin':'{} / {}'.format(move.partner_id.name, batch_picking_id.carrier_id.name)})
                move.with_context(ctx).action_force_assign_picking()
        else:
            raise exceptions.ValidationError("This pack is empty!") 
        
        self.env['stock.quant.package'].browse(package_id).write({
            'stock_batch_id': batch_picking_id.id
        })
        return

    @api.model
    def delete_package_from_batch(self, package_id):
        move_lines = self.env['stock.quant.package'].browse(package_id).move_line_ids
        picking_ids = move_lines.mapped('move_id').mapped('picking_id')
        for picking_id in picking_ids:
            self.env['stock.picking'].browse(picking_id.id).write({
                'batch_picking_id' : False
            })
        self.env['stock.quant.package'].browse(package_id).write({
            'stock_batch_id' : False
        })
        for line in move_lines:
            self.env['stock.move.line'].browse(line.id).write({
                'picking_id': False
            })
            self.env['stock.move'].browse(line.move_id.id).write({
                'picking_id': False
            })  
