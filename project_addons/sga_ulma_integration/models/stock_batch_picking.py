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
            'momcre': datetime.datetime.now(),
            'mmmbatch': self.name[-9:],
            'mmmmomexp': datetime.datetime.now(),
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

    @api.multi
    def get_from_ulma(self):
        ulma_confirmed_pickings = self.env['ulma.packinglist'].search([('status', '=', 'P')])
        for pick in ulma_confirmed_pickings:            
            data = self.env['ulma.mmminp'].search([('mmmacccolcod', '=', pick.id), ('mmmres', '=', 'FIN')])
            ulma_obj = self.env['ulma.mmminp'].browse(data.id)
            real_picking = self.env['stock.picking'].browse(pick.id)
            
            if ulma_obj.mmmcmdref == 'ERR':
                real_picking.update({
                    'sga_state': 'import_error'
                })
            elif ulma_obj.mmmcmdref == 'SAL':
                ulma_move_lines_ids = self.env['ulma.mmminp'].search([('mmmacccolcod', '=', pick.id), ('mmmres', 'not in', ['FIN', 'FINCNT'])])
                for ulma_move in ulma_move_lines_ids:
                    move_line = self.env['stock.move.line'].browse(ulma_move.mmmsecada)
                    if move_line.sga_state not in ['done', 'cancel']:
                        if move_line.ordered_qty == ulma_move.mmmcanuni:
                            move_line._set_quantity_done(ulma_move.mmmcanuni)
                            move_line.update({
                                'sga_state': 'done'
                            })
                        
                        else:
                            diference = move_line.ordered_qty - ulma_move.mmmcanuni
                            move_line.move_id._split(diference)
                            move_line._set_quantity_done(ulma_move.mmmcanuni)
                            move_line.update({
                                'sga_state': 'done'
                            })
            pick.update({
                'status': '2'
            })
            # sga_auto_validate está en sga_adaia_integration. Mirar de meterlo en un sitio del que dependan ambos
            if pick.picking_type_id and pick.picking_type_id.sga_auto_validate:
                    ctx = pick._context.copy()
                    ctx.update(from_sga=True)
                    pick.with_context(ctx).button_validate()