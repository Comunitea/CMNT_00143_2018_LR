# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPickingToDelivery(models.TransientModel):
    _name = 'stock.picking.to.delivery'
    _description = 'Add pickings to a batch picking'

    delivery_batch_id = fields.Many2one('stock.delivery.batch', string='Delivery Batch', oldname="wave_id")

    @api.multi
    def attach_pickings(self):
        # use active_ids to add picking line to the selected batch
        self.ensure_one()
        picking_ids = self.env.context.get('active_ids')
        return self.env['stock.picking'].browse(picking_ids).write({'delivery_batch_id': self.batch_id.id})
