# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockDeliveryBatch(models.Model):
    _inherit = 'stock.batch.picking'

    @api.multi
    def print_rda_delivery(self):

        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return self.env.ref('adr_product.delivery_batch_adr_report').with_context(active_ids=active_ids, active_model='stock.batch.picking', pickings=pickings).report_action([])
    

class StockBatchDelivery(models.Model):
    _inherit = 'stock.batch.delivery'

    @api.multi
    def print_rda_delivery(self):
        self.ensure_one()
        move_ids = self.env['stock.move'].search([('batch_delivery_id', '=', self.id)]).filtered(lambda x: x.quantity_done >0)
        if not move_ids:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return {'type': 'ir.actions.report','report_name': 'adr_product.batch_delivery_adr_view','report_type':"qweb-pdf",'data': None, 'docids' : active_ids}