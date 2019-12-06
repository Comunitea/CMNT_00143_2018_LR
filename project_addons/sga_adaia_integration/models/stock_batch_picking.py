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
            batch.adaia_picking_ids = batch.move_line_ids.mapped('picking_id')

    sga_state = fields.Selection(SGA_STATES)
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
                batch.adaia_dock = 102
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

    def button_new_adaia_file(self, ctx):
        return self.with_context(ctx).new_adaia_file()    

    @api.multi    
    def new_adaia_file(self, sga_file_type='BPP0', operation=False, code_type=0):
        ctx = dict(self.env.context)
        
        if operation:
            ctx['ACCION'] = operation
        if 'ACCION' not in ctx:
            ctx['ACCION'] = 'MO'

        ctx['PREFIX'] = self.picking_type_id.sga_prefix
        ctx['batch_picking_id'] = self.id
        ctx['batch_picking_name'] = self.name
        
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
        for batch in self.filtered(lambda x: x.picking_type_id.sga_integration_type == 'sga_adaia' and x.state not in ('done', 'cancel')):
            batch.new_adaia_file()
        return super().send_to_sga()