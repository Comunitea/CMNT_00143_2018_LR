# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from .res_config import SGA_STATES

class ResPartner(models.Model):

    _inherit ='res.partner'
    
    partner_type = fields.Char(compute="_compute_partner_type")
    sga_state = fields.Selection(SGA_STATES)

    @api.model
    def _compute_partner_type(self):
        for partner in self:
            if not partner.customer and not partner.supplier:
                partner.partner_type = 'TRA'
            elif partner.customer:
                partner.partner_type = 'CLI'
            elif partner.supplier:
                partner.partner_type = 'PRO'

    @api.multi
    def create_new_adaia_file_button(self):
        ctx = dict(self.env.context)
        file_type_stng = 'sga_adaia_integration.' + ctx['file_type']
        file_type = self.env['ir.config_parameter'].get_param(file_type_stng)
        for pick in self:
            pick.new_adaia_file(file_type, ctx['mod_type'], ctx['version'])
            if ctx['mod_type'] == 'DE':
                self.env['res.partner'].browse(pick.id).write({'sga_state': 'no_integrated'})

    @api.multi
    def new_adaia_file(self, sga_file_type='TE0', operation=False, force=False):
        ctx = dict(self.env.context)
        ctx['PREFIX'] = self.env['ir.config_parameter'].get_param('sga_adaia_integration.adaia_partner_prefix')
        if operation:
            ctx['ACCION'] = operation
        if 'ACCION' not in ctx:
            ctx['ACCION'] = 'AG'
        partner_ids = []

        for partner in self:
            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('res.partner', partner.id, sga_file_type)
            if new_sga_file:
                partner_ids.append(partner.id)

        if partner_ids and operation is not 'DE':
            self.env['res.partner'].browse(partner_ids).write({'sga_state': 'done'})
        elif not partner_ids:
            raise ValidationError("No hay partners para enviar a Adaia")
        return True

    @api.onchange('name', 'display_name', 'partner_type', 'street', 'city', 'state', 'country', 'zip', 'mobile', 'fax', 'email')
    def onchange_info(self):
        for partner in self:
            partner.write({'sga_state': 'no_send'})