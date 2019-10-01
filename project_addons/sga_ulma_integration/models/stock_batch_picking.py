# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError


class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"

    def get_ulma_vals(self):
        vals = self.picking_type_id.get_ulma_vals('pick')
        update_vals= {
            'momcre': fields.datetime.now().date().strftime('%Y-%m-%d'),
            'mmmbatch': self.name[9:],
            'mmmmomexp': self.date
        }
        vals.update(update_vals)
        return vals

    @api.multi
    def send_to_sga(self):
        for batch in self:
            if batch.picking_type_id.sga_integration_type == 'sga_ulma':
                batch.new_ulma_record()
        return super().send_to_sga()

    def new_ulma_record(self):
        ulma_out = self.env['ulma.mmmout']
        for batch in self.filtered(lambda x: x.picking_type_id.sga_integration_type == 'sga_ulma'):
            cont = 0
            #creo la cabecera del batch
            vals = batch.get_ulma_vals()
            batch_out = self.env['ulma.mmmout'].create(vals)
            if not batch_out:
                raise ValueError ('Error al enviar la cabecera del batch')
            line_ids = batch.draft_move_lines.filtered(lambda x: (x.state == 'assigned' or x.state == 'partially_available') and x.sga_state == 'no_send')
            sale_ids = line_ids.mapped('sale_id')
            for sale in sale_ids:
                #creo la cabecera del pedido
                vals = sale.get_sale_to_ulma(batch)
                ulma_sale = ulma_out.create(vals)
                if not ulma_sale:
                    raise ValueError ('Error al enviar la cabecera del pedido')
                for move in line_ids.filtered(lambda x: x.sale_id == sale).mapped('move_line_ids'):
                    vals = move.get_move_line_ulma_vals(cont=cont)
                    ulma_move = ulma_out.create(vals)
                    cont += 1
                line_ids.write({'sga_state': 'pending'})
            batch.sga_state = batch.picking_type_id.get_parent_state(line_ids)
        return super().send_to_sga()







