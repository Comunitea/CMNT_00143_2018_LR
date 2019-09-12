# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockBatchPickingCreator(models.TransientModel):

    _inherit = 'stock.batch.picking.creator'

    picking_type_id = fields.Many2one(string='Picking type', comodel_name='stock.picking.type', required=True, readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        domain = [
            ('id', 'in', self.env.context['active_ids']),
            ('batch_picking_id', '=', False),
            ('state', 'not in', ('cancel', 'done')),
        ]
        result = self.env['stock.picking'].read_group(domain, ['picking_type_id'], ['picking_type_id'])
        if len(result)==1:
            res['picking_type_id'] = result[0]['picking_type_id'][0]
        else:
            raise UserError (_('Non available picks or incorrect state'))
        return res

    def _prepare_stock_batch_picking(self):
        res = super()._prepare_stock_batch_picking()
        res.update(picking_type_id = self.picking_type_id.id)
        return res