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

    def apply_move_lines(self, line_vals):
        ##recuperar todos los stock_moves
        ##anular sus move_line
        ##recrear move_lines
        def prepare_line_vals(move):
            vals = {
                'move_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'picking_id': move.picking_id.id,
                'sga_state': 'done'

            }
            return vals
        
        ids = [x['move_id'] for x in line_vals]
        move_ids = self.env['stock.move'].search([('id','in', ids)])
        move_line_ids = self.env['stock.move.line']
        move_ids._do_unreserve()
        
        for val in line_vals:
            move_id = move_ids.filtered(lambda x:x.id == val['move_id'])
            move_line_vals = prepare_line_vals(move_id)
            move_line_vals.update(qty_done = float(val['qty_done']))
            move_line_ids |= move_line_ids.create(move_line_vals)
            
        return move_line_ids  

    @api.multi
    def get_from_ulma(self):
        activated = self.env['ir.config_parameter'].get_param('sga_ulma_integration.ulma_activated', False)

        picks_to_validate = self.env['stock.picking'].get_picks_ulma_pending()

        if not picks_to_validate:
            _logger.info("No se han encontrado registros sin procesar.")
        else:
            #sql_select = "select id, mmmcmdref, mmmacccolcod, mmmres, mmmcanuni, mmmsecada from ulma_mmminp where mmmacccolcod in (select id from ulma_packinglist where status = 'P') order by momcre desc limit 25"
            if len(picks_to_validate) > 1:
                sql_select = "select id, mmmcmdref, mmmacccolcod, mmmres, mmmcanuni, mmmsecada from ulma_mmminp where mmmacccolcod in {}".format(tuple(picks_to_validate.ids))
            else:
                sql_select = "select id, mmmcmdref, mmmacccolcod, mmmres, mmmcanuni, mmmsecada from ulma_mmminp where mmmacccolcod = {}".format(picks_to_validate.id)
            _logger.info("Ejecutando consulta {}".format(sql_select))         
            self._cr.execute(sql_select)

            ulma_confirmed_pickings = self._cr.fetchall()
            
            _logger.info("Registros sin procesar encontrados: {}".format(len(ulma_confirmed_pickings)))

            filtered_list = filter(lambda x: x[3] == 'FIN', ulma_confirmed_pickings)
            batch_ids = []
            move_ids = self.env['stock.move']
            for pick in filtered_list:
                line_values = []
                domain =[('id', '=', int(pick[2]))]
                real_picking = self.env['stock.picking'].search(domain, limit=1)
                if not real_picking:
                    _logger.info("\n------------ \n ERROR Procesando el picking con ID: {}\n ---------------".format(real_picking.id))
                    continue
                _logger.info("Procesando el picking con ID: {}".format(real_picking.id))
                if pick[1] == 'ERR':
                    _logger.info("\n------------ \n Picking {} devuelto con error.\n--------------".format(real_picking.id))
                    real_picking.update({
                        'sga_state': 'import_error'
                    })
                elif pick[1] == 'SAL':
                    ulma_move_lines_ids = filter(lambda x: x[3] not in ('FIN', 'FINCNT') and x[2] == pick[2], ulma_confirmed_pickings)
                    for ulma_move in ulma_move_lines_ids:
                        move_line = self.env['stock.move'].browse(int(ulma_move[5]))
                        if not move_line:
                            _logger.info("\n------------ \n ERROR Procesando el MOVIMIENTO con ID: {}\n ---------------".format(int(ulma_move[5])))
                            continue
                        
                        if move_line.state != 'done' and move_line.sga_state not in ['done', 'cancel']:
                            _logger.info("Confirmando cantidad del move: {} con cantidad {}.".format(int(ulma_move[5]), ulma_move[4]))
                            move_ids |= move_line
                            move_line = {'move_id': move_line.id, 'qty_done': ulma_move[4]}
                            line_values.append(move_line)
                        else:
                            _logger.info("\n------------ \n ERROR de estado en el MOVIMIENTO con ID: {}\n ---------------".format(int(ulma_move[5])))

                if line_values:
                    _logger.info("Proceso las move_line_ids: {}.".format(line_values))
                    move_line_ids = self.apply_move_lines(line_values)
                    _logger.info("Procesadas las move_line_ids: {}.".format(move_line_ids))

                _logger.info("Actualizando estado del pick {} a procesado.".format(real_picking.id))
                if activated:
                    sql_update = "update ulma_packinglist set ('status') values (2) where id = {}".format(int(pick[2]))
                    self._cr.execute(sql_update)
                    done = self._cr.fetchall()
                self.create({
                    'picking_id': real_picking.id
                })
                #Descomentar cuando sea seguro probar
                # sga_auto_validate está en sga_adaia_integration. Mirar de meterlo en un sitio del que dependan ambos
                batch_ids = move_ids.mapped('draft_batch_picking_id').filtered(lambda x: x.picking_type_id.autovalidate)
                if batch_ids:
                    _logger.info("Validando stock batch picking con ID: {} / {}.".format(batch_ids.id, batch.name))
                    ctx = batch._context.copy()
                    ctx.update(from_sga=True)
                    batch_ids.with_context(ctx).action_transfer()
