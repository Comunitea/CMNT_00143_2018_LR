# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time, logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MOVES_STATES_TO_SEND = ['assigned', 'partially_available']
SGA_STATES_TO_SEND = ['no_send', 'export_error', 'import_error']

class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"

    def get_ulma_vals(self):
        vals = self.picking_type_id.get_ulma_vals('pick')
        update_vals= {
            'momcre': "'{}'".format(datetime.datetime.now()),
            'mmmbatch': self.name[-9:],
            'mmmmomexp': "'{}'".format(datetime.datetime.now()),
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
        batch_outs = []
        pick_outs = []
        move_outs = []

        for batch in self.filtered(lambda x: x.sga_state == 'no_send'):
            cont = 0
            #creo la cabecera del batch
            vals = batch.get_ulma_vals()

            line_ids = batch.draft_move_lines.filtered(
                lambda x: x.state in MOVES_STATES_TO_SEND and x.sga_state in SGA_STATES_TO_SEND)
            if not line_ids:
                continue

            picking_ids = line_ids.mapped('picking_id')
            if not picking_ids:
                continue

            batch_out_id = ulma_out.create(vals)
            if not batch_out_id:
                _logger.info("Error al procesar el  batch {}".format(batch.name))
                batch_out_id.unlink()
                continue

            for pick in picking_ids:
                vals = pick.get_vals_picking_to_ulma(batch)
                ulma_pick = ulma_out.create(vals)
                pick_lines = line_ids.filtered(lambda x: x.picking_id == pick).mapped('move_line_ids')
                for move in pick_lines:
                    vals = move.get_move_line_ulma_vals(cont=cont)
                    ulma_move = ulma_out.create(vals)
                    cont += 1
                    move_outs += ulma_move
                line_ids.write({'sga_state': 'pending'})

        return super().send_to_sga()