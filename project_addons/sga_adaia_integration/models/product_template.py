# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from .res_config import SGA_STATES

class ProductProduct(models.Model):

    _inherit ='product.template'
    
    sga_state = fields.Selection(SGA_STATES)

    @api.multi
    def create_new_adaia_file_button(self):
        ctx = dict(self.env.context)
        file_type_stng = 'sga_adaia_integration.' + ctx['file_type']
        file_type = self.env['ir.config_parameter'].get_param(file_type_stng)
        for pick in self:
            pick.new_adaia_file(file_type, ctx['mod_type'], ctx['version'])
            if ctx['mod_type'] == 'DE':
                self.env['product.template'].browse(pick.id).write({'sga_state': 'NI'})

    @api.multi
    def new_adaia_file(self, sga_file_type='PRT0', operation=False, force=False):
        ctx = dict(self.env.context)
        ctx['PREFIX'] = self.env['ir.config_parameter'].get_param('sga_adaia_integration.adaia_product_template_prefix')
        if operation:
            ctx['ACCION'] = operation
        if 'ACCION' not in ctx:
            ctx['ACCION'] = 'AG'
        product_ids = []

        for product in self:
            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('product.template', product.id, sga_file_type)
            if new_sga_file:
                product_ids.append(product.id)

        if product_ids and operation is not 'DE':
            self.env['product.template'].browse(product_ids).write({'sga_state': 'SR'})
        elif not product_ids:
            raise ValidationError("No hay partners para enviar a Adaia")
        return True

    @api.onchange('volume')
    def onchange_volume(self):
        for template in self:
            template.write({'sga_state': 'NE'})