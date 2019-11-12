# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from .res_config import SGA_STATES

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
                pick.adaia_dock = 110
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


    def button_move_to_done(self):
        return self.move_to_done

    @api.multi
    def move_to_done(self):
        picks = self.filtered(lambda x: x.sga_state != 'no_integrated')
        picks.write({'sga_state': 'done'})


    def button_move_to_NE(self):
        return self.move_to_NE

    @api.multi
    def move_to_NE(self):
        sga_states_to_NE = ('pending', 'import_error', 'export_error', 'done', 'cancel', False)
        picks = self.filtered(lambda x: x.sga_integrated and x.sga_state in sga_states_to_NE)
        picks.write({'sga_state': 'no_send'})

    def button_new_adaia_file(self, ctx):
        return self.with_context(ctx).new_adaia_file()

    @api.multi
    def create_new_adaia_file_button(self):
        ctx = dict(self.env.context)
        file_type_stng = 'sga_adaia_integration.' + ctx['file_type']
        file_type = self.env['ir.config_parameter'].get_param(file_type_stng)
        for pick in self:
            pick.new_adaia_file(file_type, ctx['mod_type'], ctx['version'])
            if ctx['mod_type'] == 'DE':
                self.env['stock.picking'].browse(pick.id).write({'sga_state': 'no_integrated'})

    @api.multi    
    def new_adaia_file(self, sga_file_type='INR0', operation=False, code_type=0):
        ctx = dict(self.env.context)
        
        if operation:
            ctx['ACCION'] = operation
        if 'ACCION' not in ctx:
            ctx['ACCION'] = 'AG'

        self = self.filtered(lambda x: x.sga_state == 'no_send')
        states_to_check = ('confirmed', 'partially_available')
        states_to_send = 'assigned'
        picks = []
        pick_to_check = self.filtered(lambda x: x.state in states_to_check)
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

        for pick in self.filtered(lambda x: x.state in states_to_send):
            ctx['PREFIX'] = pick.picking_type_id.sga_prefix
            if not pick.partner_id:
                raise UserError("No puedes enviar un albarán sin asociarlo a una empresa")

            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('stock.picking', pick.id, pick.picking_type_id.sgavar_file_id.code)
            if new_sga_file:
                picks.append(pick.id)

        if picks:
            self.env['stock.picking'].browse(picks).write({'sga_state': 'pending'})
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

    def import_adaia_OUT(self, file_id):
        res = False
        pick_obj = self.env['stock.picking']
        #pick_obj = self.env['stock.batch.picking']
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        sgavar = self.env['sgavar.file'].search([('code', '=', 'OUT'), ('version', '=', 1)])
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
            print(line)
            if '|' in line:
                file_data = line.rsplit('|')
                TIPEREG = file_data[0]
                EXPORDREF = file_data[2]
            n_line += 1
            
            if TIPEREG == 'CECA':

                EXPORDREF = EXPORDREF.rsplit('.', 1)[1]
                actual_pick = self.env['stock.picking'].search([('id', '=', EXPORDREF), ('state', 'in', ['assigned', 'waiting', 'confirmed']),
                ('sga_state', 'in', ['pending'])])
                #actual_pick = self.env['stock.picking'].search([('name', '=', EXPORDREF), ('state', 'in', ['assigned', 'waiting', 'confirmed']),
                 #('sga_state', 'in', ['pending'])])

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
                    if '|' in line:
                        file_data = line.rsplit('|')
                        EXPORDLIN = file_data[3]
                        CANSER = float(file_data[6])
                    actual_line = self.env['stock.move.line'].search([('id', '=', EXPORDLIN)])
                    if not actual_line:
                        error_message = u'Op %s no encontrada en el albarán %s' % (EXPORDLIN, actual_pick.name)
                        self.create_sga_file_error(sga_file_obj, n_line,'OUT',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        if actual_line.ordered_qty == CANSER:
                            actual_line._set_quantity_done(CANSER)

                        else:
                            diference = actual_line.ordered_qty - CANSER
                            actual_line.move_id._split(diference)
                            actual_line._set_quantity_done(CANSER)
                            actual_line.write({
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
                        self.create_sga_file_error(sga_file_obj, n_line,'OUT',actual_pick,'Op no encontrada', error_message)
                        bool_error = False
                        continue
                    else:
                        package = self.env['stock.quant.package'].search([('name', '=', CNTDORREF)])
                        if not package:
                            package = self.env['stock.quant.package'].create({
                                'name': CNTDORREF,
                                'shipping_type': actual_line.move_id.shipping_type
                            })
                            
                        actual_line.update({
                            'result_package_id': package.id
                        })

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
                #pick_id = self.env['stock.batch.picking'].browse(pick.id)
                pick_id.write({
                    'sga_state': 'done'
                })
                if pick.picking_type_id and pick.picking_type_id.sga_auto_validate:
                    ctx = pick._context.copy()
                    ctx.update(from_sga=True)
                    pick.with_context(ctx).button_validate()

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