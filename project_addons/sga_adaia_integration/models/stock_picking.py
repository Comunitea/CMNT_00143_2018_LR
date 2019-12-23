# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from .res_config import SGA_STATES
import logging

_logger = logging.getLogger(__name__)

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
    sga_state = fields.Selection(SGA_STATES)

    do_backorder = fields.Selection([('default', 'Por defecto'), ('yes', 'Si'), ('no', 'No')], "Crea entrega parcial", default='default')
    sga_integrated = fields.Boolean(related="picking_type_id.sga_integrated")
    sga_integration_type = fields.Selection(related="picking_type_id.sga_integration_type")

    sga_adaia_picking_name = fields.Char(compute="compute_adaia_picking_name")
    sga_adaia_partner_ref = fields.Char(compute="compute_adaia_partner_ref")

    adaia_move_ids = fields.One2many('stock.move', compute='get_adaia_lines')
    adaia_code = fields.Char(compute="compute_route_fields")
    adaia_dock = fields.Integer(compute="compute_route_fields")    
    adaia_group = fields.Char(compute="compute_adaia_group")


    @api.multi
    @api.depends('adaia_move_ids.shipping_type', 'adaia_move_ids.delivery_route_path_id', 'adaia_move_ids.carrier_id')
    def compute_route_fields(self):
        for pick in self:
            if pick.shipping_type == 'route':
                pick.adaia_code = 'NORM'
                pick.adaia_dock = 102
            elif pick.shipping_type == 'pasaran':
                pick.adaia_code = 'PAS'
                pick.adaia_dock = 107
            else:
                pick.adaia_code = 'AG'
                pick.adaia_dock = 106

    @api.multi
    @api.depends('adaia_move_ids')
    def compute_adaia_group(self):
        for pick in self:
            if len(pick.adaia_move_ids) < 4:
                pick.adaia_group = 'MP'
            else:
                pick.adaia_group = ''

    @api.multi
    def get_adaia_lines(self):
        batch_picking_id = self._context.get('draft_batch_picking_id', False)
        if batch_picking_id:
            for pick in self:
                domain = [('draft_batch_picking_id', '=', batch_picking_id), ('picking_id', '=', pick.id),
                 ('state', 'in', ('assigned', 'partially_available')), ('sga_state', '=', 'no_send')]
                move_ids = self.env['stock.move'].search(domain)
                pick.adaia_move_ids = move_ids
    

    @api.multi
    def compute_adaia_picking_name(self):
        batch_picking_id = self._context.get('draft_batch_picking_id', False)
        if batch_picking_id:
            for pick in self:
                pick.sga_adaia_picking_name = "{}.{}".format(self._context.get('draft_batch_picking_name', pick.name), pick.id)

    @api.multi
    @api.depends('partner_id')
    def compute_adaia_partner_ref(self):
        for pick in self:
            partner_ref = pick.partner_id.ref if pick.partner_id else self.env['purchase.order'].\
            search([('name', '=', pick.origin)], limit=1).partner_id.ref
            pick.sga_adaia_partner_ref = "{}{}".format(8, partner_ref)

    def force_button_validate(self):
        self.sga_state = 'done'
        return self.button_validate()

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id.sga_integrated:
            self.sga_state = 'no_send'
        else:
            self.sga_state = 'no_integrated'
        return super(StockPickingSGA, self).onchange_picking_type()

    @api.model
    def create(self, vals):
        if vals['picking_type_id']:
            picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if picking_type:
                if picking_type.sga_integrated:
                    vals['sga_state'] = "no_send"
                else:
                    vals['sga_state'] = "no_integrated"
        pick = super(StockPickingSGA, self).create(vals)
        return pick

    def check_write_in_pm(self, vals):

        fields_to_check = ('launch_pack_operations', 'pack_operation_product_ids', 'move_lines',
                           'recompute_pack_op')

        fields_list = sorted(list(set(vals).intersection(set(fields_to_check))))
        if len(self.filtered(lambda x: x.sga_state == 'pending')) and fields_list:
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


    def apply_move_lines(self, line_vals, code):
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
            if val['result_package_id'] and code == 'INR':
                move_line_vals.update(result_package_id=val['result_package_id'])
            move_line_ids |= move_line_ids.create(move_line_vals)
            
        return move_line_ids  

    def import_adaia(self, file_id, code):

        def get_picking_from_line(n_line, codigo):
            codigo = codigo.rsplit('.', 1)[1]            
            domain = [('id', '=', codigo), ('state', 'in', ['assigned', 'waiting', 'confirmed'])]
            pick = self.env['stock.picking'].search(domain, order = 'id desc', limit=1)
            _logger.info("Procesando el picking: {}".format(pick))
            if not pick:
                bool_error = False
                str_error += "Codigo de albaran %s no encontrado o estado incorrecto en linea ...%s " % (codigo, n_line)
                error_message =  u'Albarán %s no encontrado o en estado incorrecto.' % (codigo)
                _logger.info("Error: {}".format(error_message))
                self.create_sga_file_error(sga_file_obj, n_line, 'INR', pick, 'Pick no válido', error_message)
                sga_file_obj.write_log(str_error)
            return pick
    
        def get_stock_move_from_line(n_line, actual_pick, line, code='INR'):
            if code=='INR':
                vals={}
                file_data = line.rsplit('|')
                RECORDREF = file_data[2]
                CANREC = float(file_data[4])
                RECORDLIN = file_data[9]
                actual_line = self.env['stock.move'].search([('id', '=', RECORDLIN)])
                _logger.info("Procesando la move line: {}".format(actual_line))
                if not actual_line:
                    error_message = u'Op línea %s no encontrada en el albarán %s' % (RECORDLIN, actual_pick.name)
                    _logger.info("Error: {}".format(error_message))
                    self.create_sga_file_error(sga_file_obj, n_line,'INR',actual_pick,'Op no encontrada', error_message)
                    bool_error = False
                else:
                    _logger.info("Encontrada línea: {} con cantidad: {}".format(actual_line.id, CANREC))
                    vals = {
                        'move_id': actual_line.id,
                        'qty_done': CANREC,
                        'move_line_ids': []
                    }
                    sga_ops_exists.append(actual_line.id)
                return vals
            
            if code=='OUT':
                vals={}
                file_data = line.rsplit('|')
                EXPORDLIN = file_data[3]
                CANSER = float(file_data[6])
                actual_line = self.env['stock.move'].search([('id', '=', EXPORDLIN)])
                _logger.info("Procesando la move line: {}".format(actual_line))
                if not actual_line:
                    error_message = u'Op línea %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                    _logger.info("Error: {}".format(error_message))
                    self.create_sga_file_error(sga_file_obj, n_line,'OUT',actual_pick,'Op no encontrada', error_message)
                    bool_error = False
                else:
                    _logger.info("Encontrada línea: {} con cantidad: {}".format(actual_line.id, CANSER))

                    vals = {
                        'move_id': actual_line.id,
                        'qty_done': CANSER,
                        'move_line_ids': []
                    }

                    sga_ops_exists.append(actual_line.id)
                return vals


        def get_move_line_from_line(n_line, actual_pick, line, code='INR'):
            if code=='INR':
                CNTDORREF = line.rsplit('|')[4]
                QTY = line.rsplit('|')[8]
                RECORDLIN = line.rsplit('|')[19]

                _logger.info("Container: {}, línea: {}".format(CNTDORREF, RECORDLIN))
                actual_line = self.env['stock.move'].search([('id', '=', RECORDLIN)])
                if not actual_line:
                    error_message = u'Op línea %s no encontrada en el albarán %s' % (RECORDLIN, actual_pick.name)
                    _logger.info("Error: {}".format(error_message))
                    self.create_sga_file_error(sga_file_obj, n_line,'INR',actual_pick,'Op no encontrada', error_message)
                    bool_error = False
                else:
                    move_line_id = {'move_id': int(RECORDLIN), 'qty_done': QTY}

                    package = self.env['stock.quant.package'].search([('name', '=', CNTDORREF)])
                    if not package:
                        package = self.env['stock.quant.package'].create({
                            'name': CNTDORREF
                        })
                        _logger.info("Creado paquete: {} con matrícula: {}".format(package.id, package.name))
                    move_line_id.update({
                        'result_package_id': package.id
                    })

                    print("INR: {}".format(move_line_id))

                    return move_line_id

            if code=='OUT':
                EXPORDLIN = line.rsplit('|')[19]
                CNTDORREF = line.rsplit('|')[4]
                CAN = line.rsplit('|')[8]
                
                _logger.info("Container: {}, línea: {}".format(CNTDORREF, EXPORDLIN))
                actual_line = self.env['stock.move'].search([('id', '=', EXPORDLIN)])
                
                if not actual_line:
                    error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                    self.create_sga_file_error(sga_file_obj, n_line,'OUT',actual_pick,'Op no encontrada', error_message)
                    bool_error = False
                else:
                    move_line_id = {'move_id': int(EXPORDLIN), 'qty_done': CAN}
                    package = self.env['stock.quant.package'].search([('name', '=', CNTDORREF)])
                    if not package:
                        package = self.env['stock.quant.package'].create({
                            'name': CNTDORREF,
                            'shipping_type': actual_line.shipping_type
                        })
                        
                    move_line_id.update({
                        'result_package_id': package.id
                    })

                    print("OUT: {}".format(move_line_id))

                    return move_line_id

        res = False
        pick_obj = self.env['stock.picking']
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        sgavar = self.env['sgavar.file'].search([('code', '=', code), ('version', '=', 1)])
        pick = False
        if not sgavar:
            raise ValidationError("Modelo no encontrado")
        create = False
        sga_ops_exists = []
        do_pick = False
        pool_ids = []
        actual_pick = False
        pick_pool = []
        cnt_pool = []
        _logger.info("Importando fichero con código: {}".format(code))
        line_values = []
        package_values = []
        for line in sga_file_lines:
            if not '|' in line :
                _logger.info("Formato incorrecto en {} la línea\n{}".format(sga_file.name, n_line))
                continue
            if code == 'OUT':
                ### ALBARANES DE SALIDA
                if '|' in line:
                    file_data = line.rsplit('|')
                    TIPEREG = file_data[0]
                    EXPORDREF = file_data[2]
                n_line += 1
                
                if TIPEREG == 'CECA':
                    ### DATOS DE ALBARÁN. STOCK.PICKING
                    actual_pick = get_picking_from_line(n_line, EXPORDREF)
                    if not actual_pick:
                        coninue
                    pick_pool.append(actual_pick)
                    continue

                if not actual_pick:
                    continue

                if TIPEREG == 'CELI':
                    ##DATOS DE LA LINEA. STCOK_MOVE_LINE
                    vals = get_stock_move_from_line(n_line, actual_pick, line, code)

                elif TIPEREG == 'CECN':
                    ##DATOS DEL PAQUETE. STOCK.QUANT_PACKAGE
                    
                    line_vals = get_move_line_from_line(n_line, actual_pick, line, code)
                    print("line_vals: {}".format(line_vals))
                    if line_vals:
                        line_values.append(line_vals)
                

            if code == 'INR':
                ##ALBARANES DE ENTRADA
                if '|' in line:
                    file_data = line.rsplit('|')
                    TIPEREG = file_data[0]
                    RECORDREF = file_data[4]
                n_line += 1

                if TIPEREG == 'CRCA':
                    ##DATOS DE ALBARAN. STOCK_PICKING
                    actual_pick = get_picking_from_line(n_line, RECORDREF)
                    if not actual_pick:
                        coninue
                    pick_pool.append(actual_pick)
                    continue

                if not actual_pick:
                    continue

                if TIPEREG == 'CRLI':
                    ##DATOS DE LA LINEA. STCOK_MOVE_LINE
                    vals = get_stock_move_from_line(n_line, actual_pick, line, code)

                elif TIPEREG == 'CRCN':
                    ##DATOS DEL PAQUETE. STOCK.QUANT_PACKAGE
                    
                    line_vals = get_move_line_from_line(n_line, actual_pick, line, code)
                    print("line_vals: {}".format(line_vals))
                    if line_vals:
                        line_values.append(line_vals)

        if line_values:
            print("line_values: {}".format(line_values))
            move_line_ids = self.apply_move_lines(line_values, code)
            print("move_line_ids: {}".format(move_line_ids))
            picking_ids = move_line_ids.mapped('picking_id')
            print("picking_ids: {}".format(picking_ids))
        
        batch_ids = picking_ids.mapped('draft_batch_picking_id')
        print("batch_ids: {}".format(batch_ids))
        for batch in batch_ids:
            if batch.picking_type_id and batch.picking_type_id.sga_auto_validate:
                _logger.info("Validando stock batch picking con ID: {} / {}.".format(batch_ids.id, batch.name))
                ctx = batch._context.copy()
                ctx.update(from_sga=True)
                batch.with_context(ctx).action_transfer()
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