# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time, logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"

    def get_ulma_vals(self):
        vals = self.picking_type_id.get_ulma_vals('pick')
        update_vals= {
            'momcre': datetime.datetime.now(),
            'mmmbatch': self.name[-9:],
            'mmmmomexp': datetime.datetime.now()
        }
        vals.update(update_vals)
        return vals

    @api.multi
    def send_to_sga(self):
        for batch in self.filtered(lambda x: x.picking_type_id.sga_integration_type == 'sga_ulma' and x.state not in ('done', 'cancel')):
            batch.new_ulma_record()
        return super().send_to_sga()

    def new_ulma_record(self):
        ulma_out = self.env['ulma.processed.mmmout']
        for batch in self.filtered(lambda x: x.picking_type_id.sga_integration_type == 'sga_ulma'):
            cont = 0
            #creo la cabecera del batch
            vals = batch.get_ulma_vals()
            batch_out = self.env['ulma.processed.mmmout'].create(vals)
            if not batch_out:
                raise ValueError ('Error al enviar la cabecera del batch')
            line_ids = batch.draft_move_lines.filtered(lambda x: (x.state == 'assigned' or x.state == 'partially_available') and x.sga_state == 'no_send')
            picking_ids = line_ids.mapped('picking_id')
            for pick in picking_ids:
                #creo la cabecera del pedido
                vals = pick.send_picking_to_ulma(batch)
                ulma_pick = ulma_out.create(vals)
                if not ulma_pick:
                    raise ValueError ('Error al enviar la cabecera del pedido')
                for move in line_ids.filtered(lambda x: x.picking_id == pick).mapped('move_line_ids'):
                    vals = move.get_move_line_ulma_vals(cont=cont)
                    ulma_move = ulma_out.create(vals)
                    cont += 1
                line_ids.write({'sga_state': 'pending'})
            batch.sga_state = batch.picking_type_id.get_parent_state(line_ids)
        return super().send_to_sga()