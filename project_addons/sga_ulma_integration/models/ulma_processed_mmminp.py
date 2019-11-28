# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)

class UlmaMmminp(models.Model):
    _name = "ulma.processed.mmminp"
    _description = "Movements from Ulma"
    
    picking_id = fields.Char(string='Picking ID')    

    @api.multi
    def get_from_ulma(self):            
        sql_select = "select id, mmmcmdref, mmmacccolcod, mmmres, mmmcanuni, mmmsecada from ulma_mmminp where mmmacccolcod in (select id from ulma_packinglist where status = 'P')"
        self._cr.execute(sql_select)
        ulma_confirmed_pickings = self._cr.fetchall()

        _logger.info("Registros sin procesar encontrados: {}".format(len(ulma_confirmed_pickings)))
        filtered_list = filter(lambda x: x[3] == 'FIN', ulma_confirmed_pickings)
        batch_ids = []
        for pick in filtered_list:
            real_picking = self.env['stock.picking'].browse(int(pick[2]))

            _logger.info("Procesando el picking con ID: {}".format(real_picking.id))
            
            if pick[1] == 'ERR':
                _logger.info("Picking {} devuelto con error.".format(real_picking.id))
                real_picking.update({
                    'sga_state': 'import_error'
                })
            elif pick[1] == 'SAL':
                ulma_move_lines_ids = filter(lambda x: x[3] not in ('FIN', 'FINCNT') and x[2] == pick[2], ulma_confirmed_pickings)
                for ulma_move in ulma_move_lines_ids:
                    move_line = self.env['stock.move.line'].browse(int(ulma_move[5]))
                    if move_line.draft_batch_picking_id:
                        batch_ids.append(move_line.draft_batch_picking_id)
                    if move_line.sga_state not in ['done', 'cancel']:
                        _logger.info("Confirmando cantidad de la línea: {} con cantidad {}.".format(ulma_move[5], ulma_move[4]))
                        if move_line.state != 'done':
                            vals = {
                                    'qty_done': ulma_move[4],
                                    'sga_state': 'done'}
                        else:
                            vals = {
                                    'qty_done': move_line.qty_done + ulma_move[4],
                                    'sga_state': 'done'}
                        move_line.write(vals)
            _logger.info("Actualizando estado del pick {} a procesado.".format(real_picking.id))
            
            sql_update = "update ulma_packinglist set ('status') values (2) where id = {}".format(pick[2])
            self.create({
                'picking_id': real_picking.id
            })
            #Descomentar cuando sea seguro probar
            self._cr.execute(sql_update)
            done = self._cr.fetchall()

            # sga_auto_validate está en sga_adaia_integration. Mirar de meterlo en un sitio del que dependan ambos
            for batch in batch_ids:
                if batch.picking_type_id and batch.picking_type_id.sga_auto_validate:
                    _logger.info("Validando stock batch picking con ID: {} / {}.".format(batch_ids.id, batch.name))
                    ctx = batch._context.copy()
                    ctx.update(from_sga=True)
                    batch.with_context(ctx).action_transfer()

            if False and real_picking.picking_type_id and real_picking.picking_type_id.sga_auto_validate:
                _logger.info("Validando stock picking con ID: {}.".format(real_picking.id))
                ctx = real_picking._context.copy()
                ctx.update(from_sga=True)
                real_picking.with_context(ctx).button_validate()