# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class StockPickingSGA(models.Model):

    _inherit = "stock.picking"

    sga_operation = fields.Selection([('A', 'Alta'), ('M', 'Modificacion'),
                                      ('B', 'Baja'), ('F', 'Modificacion + Alta')], default='A', copy=False)
    warehouse_id = fields.Many2one(related="picking_type_id.warehouse_id")
    warehouse_code = fields.Char(related="picking_type_id.warehouse_id.code")

    code = fields.Char("Sale order type code", size=30)
    description = fields.Char("Sale order type description", size=100)

    stock_picking_sgatype_id = fields.Many2one('stock.picking.sgatype', string ="Tipo de albaran/venta (SGA)")
    stock_picking_sgatype_code = fields.Char(related="stock_picking_sgatype_id.code")
    stock_picking_sgatype_description = fields.Char(related="stock_picking_sgatype_id.description")

    sga_priority = fields.Integer("Priority", default=100)

    sga_company = fields.Char(related="partner_id.name")
    sga_state = fields.Selection ([('NI', 'Sin integracion'),
                                   ('NE', 'No exportado'),
                                   ('PM', 'Pendiente Adaia'),
                                   ('EE', 'Error en exportacion'),
                                   ('EI', 'Error en importacion'),
                                   ('SR', 'Realizado'),
                                   ('SC', 'Cancelado')], 'Estado Adaia', default="NI", track_visibility='onchange', copy=False)

    do_backorder = fields.Selection([('default', 'Por defecto'), ('yes', 'Si'), ('no', 'No')], "Crea entrega parcial", default='default')
    sga_integrated = fields.Boolean(related="picking_type_id.sga_integrated")

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id.sga_integrated:
            self.sga_state = 'NE'
        else:
            self.sga_state = 'NI'
        return super(StockPickingSGA, self).onchange_picking_type()

    @api.model
    def create(self, vals):
        if vals['picking_type_id']:
            picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if picking_type:
                if picking_type.sga_integrated:
                    vals['sga_state'] = "NE"
                else:
                    vals['sga_state'] = "NI"
        pick = super(StockPickingSGA, self).create(vals)
        return pick

    def check_write_in_pm(self, vals):

        fields_to_check = ('launch_pack_operations', 'pack_operation_product_ids', 'move_lines',
                           'recompute_pack_op')

        fields_list = sorted(list(set(vals).intersection(set(fields_to_check))))
        if len(self.filtered(lambda x: x.sga_state == 'PM')) and fields_list:
            return True
        return False

    @api.multi
    def write(self, vals):
        if 'action_done_bool' in vals:
            for pick in self:
                pick.message_post(
                body="El albarán <em>%s</em> <b>ha cambiado el estado de validación automática a</b> <em>%s</em>" % (pick.name, vals['action_done_bool']))
        if self.check_write_in_pm(vals):
            raise ValidationError("No puedes modificar operaciones si está enviado a Adaia")

        return super(StockPickingSGA, self).write(vals)


    def button_move_to_done(self):
        return self.move_to_done

    @api.multi
    def move_to_done(self):
        picks = self.filtered(lambda x: x.sga_state != 'NI')
        picks.write({'sga_state': 'SR'})


    def button_move_to_NE(self):
        return self.move_to_NE

    @api.multi
    def move_to_NE(self):
        sga_states_to_NE = ('PM', 'EI', 'EE', 'SR', 'SC', False)
        picks = self.filtered(lambda x: x.sga_integrated and x.sga_state in sga_states_to_NE)
        picks.write({'sga_state': 'NE'})

    def button_new_adaia_file(self, ctx):

        return self.with_context(ctx).new_adaia_file()

    def new_adaia_file(self, operation=False, force=False):

        ctx = dict(self.env.context)
        if operation:
            ctx['operation'] = operation
        if 'operation' not in ctx:
            ctx['operation'] = 'A'
        self = self.filtered(lambda x: x.sga_state == 'NE')
        states_to_check = ('confirmed', 'partially_available')
        states_to_send = 'assigned'
        picks = []
        pick_to_check = self.filtered(lambda x: x.state in states_to_check and not force)
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

        for pick in self.filtered(lambda x: x.state in states_to_send or force):
            if not pick.partner_id:
                raise UserError("No puedes enviar un albarán sin asociarlo a una empresa")

            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('stock.picking', pick.id, pick.picking_type_id.sgavar_file_id.code)
            if new_sga_file:
                picks.append(pick.id)

        if picks:
            self.env['stock.picking'].browse(picks).write({'sga_state': 'PM'})
        else:
            raise ValidationError("No hay albaranes para enviar a Adaia")
        return True

    @api.multi
    def renum_operation_line_number(self):
        for pick in self:
            if pick.picking_type_id.sga_integrated:
                cont = 1
                for op in pick.pack_operation_product_ids:
                    op.line_number = cont
                    cont += 1

    def return_val_line(self, line, code):
        sgavar = self.env['sgavar.file'].search([('code', '=', code)])
        if not sgavar:
            raise ValidationError("Modelo no encontrado")
        st = 0
        en = 0
        val = {}

        for var in sgavar.sga_file_var_ids:
            if var.length_dec == 0:
                en = st + var.length
                val[var.name] = line[st:en].strip() or var.fillchar
                st = en
            else:
                en = st + var.length_int
                quantity_int = int(line[st:en].strip() or 0)
                st = en
                en = st + var.length_dec
                quantity_dec = int(line[st:en].strip() or 0) / 5000
                val[var.name] = quantity_int + quantity_dec
                st = en
        return val
    
    def import_adaia_INR(self, file_id):
        res = False
        pick_obj = self.env['stock.picking']
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        sgavar = self.env['sgavar.file'].search([('code', '=', 'INR'), ('version', '=', 0)])
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
            n_line += 1
            TIPEREG = line[0:4]
            EXPORDREF = line[17:33].replace(" ","")
            if TIPEREG == 'CRCA':                    

                actual_pick = self.env['stock.picking'].search([('name', '=', EXPORDREF), ('state', 'in', ['assigned', 'waiting', 'confirmed']),
                 ('sga_state', 'in', ['PM'])])

                if not actual_pick:
                    bool_error = False
                    str_error += "Codigo de albaran %s no encontrado o estado incorrecto en linea ...%s " % (EXPORDREF, n_line)
                    error_message =  u'Albarán %s no encontrado o en estado incorrecto.' % (
                                      EXPORDREF)
                    self.create_sga_file_error(sga_file_obj, n_line, 'INR', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue
                
                else:
                    pick_pool.append(actual_pick)
            
            else:
                if actual_pick is not False and TIPEREG == 'CRLI':
                    EXPORDLIN = line[78:87]
                    CANSER = line[38:47]
                    actual_line = self.env['stock.move.line'].search([('id', '=', EXPORDLIN)])
                    if not actual_line:
                        error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                        self.create_sga_file_error(sga_file_obj, n_line,'INR',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        if actual_line.qty_done == CANSER:
                            actual_line.write({
                                'qty_done': CANSER
                            })
                        else:
                            actual_line.write({
                                'qty_done': CANSER,
                                'sga_changed': 1
                            })
                        sga_ops_exists.append(actual_line.id)
                else:
                    bool_error = False
                    str_error += "Codigo de albaran no encontrado o estado incorrecto. Revisa el formato del archivo ..."
                    error_message =  u'Albarán no encontrado o en estado incorrecto. Revisa el formato del archivo.'
                    self.create_sga_file_error(sga_file_obj, n_line, 'OUT', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue

        if pick_pool:
            for pick in pick_pool:
                pick_id = self.env['stock.picking'].browse(pick.id)
                pick_id.write({
                    'sga_state': 'SR'
                })
                pick_id.button_validate()

        return pick_pool

    def import_adaia_OUT(self, file_id):
        res = False
        pick_obj = self.env['stock.picking']
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        sgavar = self.env['sgavar.file'].search([('code', '=', 'OUT'), ('version', '=', 0)])
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
            n_line += 1
            TIPEREG = line[0:4]
            EXPORDREF = line[6:20].replace(" ","")
            if TIPEREG == 'CECA':                    

                actual_pick = self.env['stock.picking'].search([('name', '=', EXPORDREF), ('state', 'in', ['assigned', 'waiting', 'confirmed']),
                 ('sga_state', 'in', ['PM'])])

                if not actual_pick:
                    bool_error = False
                    str_error += "Codigo de albaran %s no encontrado o estado incorrecto en linea ...%s " % (EXPORDREF, n_line)
                    error_message =  u'Albarán %s no encontrado o en estado incorrecto.' % (
                                      EXPORDREF)
                    self.create_sga_file_error(sga_file_obj, n_line, 'OUT', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue
                
                else:
                    pick_pool.append(actual_pick)
            
            else:
                if actual_pick is not False and TIPEREG == 'CELI':
                    EXPORDLIN = line[21:30]
                    CANSER = line[55:64]
                    actual_line = self.env['stock.move.line'].search([('id', '=', EXPORDLIN)])
                    if not actual_line:
                        error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                        self.create_sga_file_error(sga_file_obj, n_line,'OUT',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        if actual_line.qty_done == CANSER:
                            actual_line.write({
                                'qty_done': CANSER
                            })
                        else:
                            actual_line.write({
                                'qty_done': CANSER,
                                'sga_changed': 1
                            })
                        sga_ops_exists.append(actual_line.id)
                else:
                    bool_error = False
                    str_error += "Codigo de albaran no encontrado o estado incorrecto. Revisa el formato del archivo ..."
                    error_message =  u'Albarán no encontrado o en estado incorrecto. Revisa el formato del archivo.'
                    self.create_sga_file_error(sga_file_obj, n_line, 'OUT', actual_pick, 'Pick no válido', error_message)

                    sga_file_obj.write_log(str_error)
                    continue

        if pick_pool:
            for pick in pick_pool:
                pick_id = self.env['stock.picking'].browse(pick.id)
                pick_id.write({
                    'sga_state': 'SR'
                })
                pick_id.button_validate()

        #Aquí me quedé

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