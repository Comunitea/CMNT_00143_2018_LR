# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from .res_config import SGA_STATES

class StockBatchPickingSGA(models.Model):

    _inherit = "stock.batch.picking"

    @api.multi
    def get_adaia_picking_ids(self):
        for batch in self:
            batch.adaia_picking_ids = batch.draft_move_line_ids.mapped('picking_id')

    sga_state = fields.Selection(SGA_STATES)
    draft_move_line_ids = fields.One2many('stock.move.line', 'draft_batch_picking_id', string='Líneas de Movimientos')
    adaia_code = fields.Char(compute="compute_route_fields")
    adaia_dock = fields.Integer(compute="compute_route_fields")    
    adaia_group = fields.Char(compute="compute_adaia_group")
    adaia_import_partner_ref = fields.Char(compute="import_partner_ref")
    adaia_picking_ids = fields.One2many('stock.picking', compute='get_adaia_picking_ids')    


    @api.multi
    @api.depends('move_lines.shipping_type', 'move_lines.delivery_route_path_id', 'move_lines.carrier_id')
    def compute_route_fields(self):
        super(StockBatchPickingSGA, self).compute_route_fields()
        for batch in self:
            if batch.shipping_type == 'route':
                batch.adaia_code = 'NORM'
                batch.adaia_dock = 110
            elif batch.shipping_type == 'pasaran':
                batch.adaia_code = 'PAS'
                batch.adaia_dock = 107
            else:
                batch.adaia_code = 'AG'
                batch.adaia_dock = 106

    @api.multi
    @api.depends('move_lines')
    def compute_adaia_group(self):
        for batch in self:
            if len(batch.move_lines) < 4:
                batch.adaia_group = 'MP'
            else:
                batch.adaia_group = ''


    def button_move_to_done(self):
        return self.move_to_done

    @api.multi
    def move_to_done(self):
        pickings = self.mapped('picking_ids')
        picks = pickings.filtered(lambda x: x.sga_state != 'no_integrated')
        picks.update({'sga_state': 'done'})
        self.update({'sga_state': 'done'})


    def button_move_to_NE(self):
        return self.move_to_NE

    @api.multi
    def move_to_NE(self):
        sga_states_to_NE = ('pending', 'import_error', 'export_error', 'done', 'cancel', False)
        pickings = self.mapped('picking_ids')
        picks = pickings.filtered(lambda x: x.sga_integrated and x.sga_state in sga_states_to_NE)
        self.update({'sga_state': 'no_send'})
        picks.update({'sga_state': 'no_send'})

    def button_new_adaia_file(self, ctx):
        return self.with_context(ctx).new_adaia_file()

    # Only for regular batch picking (batch_picking with stock.pickings) #
    def new_adaia_file_batch_picking(self, operation=False, force=False):

        ctx = dict(self.env.context)
        if operation:
            ctx['operation'] = operation
        if 'operation' not in ctx:
            ctx['operation'] = 'A'
        pickings = self.mapped('picking_ids')
        picks_in_batch = pickings.filtered(lambda x: x.sga_state == 'no_send')
        states_to_check = ('confirmed', 'partially_available')
        states_to_send = 'assigned'
        picks = []
        pick_to_check = picks_in_batch.filtered(lambda x: x.state in states_to_check and not force)
        if pick_to_check and pick_to_check[0]:
            view = self.env.ref('sga_file.stock_adaia_confirm_wizard')
            wiz = self.env['stock.adaia.confirm'].create({'pick_id': pick_to_check.id})
            return {
                'name': 'Confirmación de envio a Adaia',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.adaia.confirm',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'res_id': wiz.id,
                'target': 'new',
                'context': self.env.context,
            }

        for pick in picks_in_batch.filtered(lambda x: x.state in states_to_send or force):
            if not pick.partner_id:
                raise UserError("No puedes enviar un albarán sin asociarlo a una empresa")

            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('stock.picking', pick.id, pick.picking_type_id.sgavar_file_id.code)
            if new_sga_file:
                picks.append(pick.id)

        if picks:
            self.update({'sga_state': 'pending'})
            self.env['stock.picking'].browse(picks).update({'sga_state': 'done'})
        else:
            raise ValidationError("No hay albaranes para enviar a Adaia")
        return True
    

    @api.multi    
    def new_adaia_file(self, sga_file_type='BPP0', operation=False, code_type=0):
        ctx = dict(self.env.context)
        
        if operation:
            ctx['ACCION'] = operation
        if 'ACCION' not in ctx:
            ctx['ACCION'] = 'MO'

        ctx['PREFIX'] = self.picking_type_id.sga_prefix
        ctx['draft_batch_picking_id'] = self.id
        ctx['draft_batch_picking_name'] = self.name
        
        states_to_check = ('confirmed', 'partially_available', 'draft', 'ready')
        states_to_send = ('assigned', 'draft', 'ready')

        if self.state in states_to_send:
            new_sga_file = self.env['sga.file'].with_context(ctx).\
                    check_sga_file('stock.batch.picking', self.id, self.picking_type_id.sgavar_file_id.code)
            if not new_sga_file:
                raise ValidationError("No hay albaranes para enviar a Adaia")
        return True

    @api.multi
    def send_to_sga(self):
        for batch in self:
            if batch.picking_type_id.sga_integration_type == 'sga_adaia':
                batch.new_adaia_file()
        return super().send_to_sga()



    def import_adaia_OUT(self, file_id):
        res = False
        pick_obj = self.env['stock.batch.picking']
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        sgavar = self.env['sgavar.file'].search([('code', '=', 'SBP'), ('version', '=', 1)])
        pick = False
        if not sgavar:
            raise ValidationError("Modelo no encontrado")
        create = False
        sga_ops_exists = []
        do_pick = False
        pool_ids = []
        actual_pick = False
        pick_pool = []
        for line in sga_file_lines:
            if '|' in line:
                file_data = line.rsplit('|')
                TIPEREG = file_data[0]
                EXPORDREF = file_data[2]
            n_line += 1
            
            if TIPEREG == 'CECA':
                #('sga_state', 'in', ['pending']) retirado porque es non-stored                    
                actual_pick = self.env['stock.batch.picking'].search([('name', '=', EXPORDREF), ('state', 'in', ['assigned', 'waiting', 'confirmed', 'draft', 'ready']),])

                if not actual_pick:
                    bool_error = False
                    str_error += "Codigo de albaran %s no encontrado o estado incorrecto en linea ...%s " % (EXPORDREF, n_line)
                    error_message =  u'Albarán %s no encontrado o en estado incorrecto.' % (
                                      EXPORDREF)
                    self.create_sga_file_error(sga_file_obj, n_line, 'SBP', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue
                
                else:
                    pick_pool.append(actual_pick)
            
            else:
                if actual_pick is not False and TIPEREG == 'CELI':
                    if '|' in line:
                        file_data = line.rsplit('|')
                        EXPORDLIN = file_data[3]
                        CANSER = file_data[6]
                        CANSER = float(CANSER)
                    actual_line = self.env['stock.move.line'].search([('id', '=', EXPORDLIN)])
                    if not actual_line:
                        error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                        self.create_sga_file_error(sga_file_obj, n_line,'SBP',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        if actual_line.ordered_qty == CANSER:
                            if actual_line.qty_done != CANSER:
                                actual_line._set_quantity_done(CANSER)

                        else:
                            diference = actual_line.ordered_qty - CANSER
                            actual_line.move_id._split(diference)
                            actual_line._set_quantity_done(CANSER)
                            actual_line.update({
                                'sga_changed': 1
                            })
                        sga_ops_exists.append(actual_line.id)

                elif actual_pick is not False and TIPEREG == 'CECN':
                    if '|' in line:
                        file_data = line.rsplit('|')
                        EXPORDLIN = file_data[19]
                        CNTDORREF = file_data[4]
                        CAN = file_data[8]
                    
                    actual_line = self.env['stock.move.line'].search([('id', '=', EXPORDLIN)])
                    if not actual_line:
                        error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                        self.create_sga_file_error(sga_file_obj, n_line,'SBP',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        package = self.env['stock.quant.package'].search([('name', '=', CNTDORREF)])
                        if not package:
                            package = self.env['stock.quant.package'].create({
                                'name': CNTDORREF,
                                'shipping_type': line_id.move_id.shipping_type
                            })
                            
                        actual_line.update({
                            'product_qty': CAN,
                            'result_package_id': package.id
                        })

                else:
                    bool_error = False
                    str_error += "Codigo de albaran no encontrado o estado incorrecto. Revisa el formato del archivo ..."
                    error_message =  u'Albarán no encontrado o en estado incorrecto. Revisa el formato del archivo.'
                    self.create_sga_file_error(sga_file_obj, n_line, 'SBP', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue

        if pick_pool:
            for pick in pick_pool:
                pick_id = self.env['stock.batch.picking'].browse(pick.id)
                pick_id.set_as_sga_done()
                if pick.picking_type_id and pick.picking_type_id.sga_auto_validate:
                    pick_id.button_validate()

        return pick_pool

    def create_sga_file_error(self, sga_file_obj, n_line, sga_operation, pick, error_code, error_message):
        error_vals = {'file_name': sga_file_obj.name,
                      'sga_file_id': sga_file_obj.id,
                      'line_number': n_line,
                      'sga_operation': sga_operation,
                      'object_type': sga_operation,
                      'object_id': pick.name,
                      'date_error': sga_file_obj.name[5:19].strip(),
                      'error_code': error_code,
                      'error_message': error_message}
        self.env['sga.file.error'].create(error_vals)