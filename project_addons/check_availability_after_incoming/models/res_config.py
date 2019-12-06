# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    delay_check_availability = fields.Boolean('Delay check availability')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter'].sudo()
        res.update({'delay_check_availability': icp.get_param('delay_check_availability')})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env['ir.config_parameter'].sudo()

        icp.set_param('delay_check_availability', self.delay_check_availability)
