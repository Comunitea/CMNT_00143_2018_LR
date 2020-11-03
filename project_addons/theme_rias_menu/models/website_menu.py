# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, http, _


class Website(models.Model):
    _inherit = 'website'

    def dynamic_category_list(self):
        domain = []
        return self.env['product.public.category'].sudo().search(domain)

    @api.multi
    def allowed_menus(self, menus):
        allowed_menus = []
        for menu in menus.filtered(lambda a: a.is_visible and a.menu_icon):
            
            allowed_menus += menu
        
        return allowed_menus

    @api.multi
    def calculate_offset(self, menus):
        if len(menus) < 6:
            return 'col-md-offset-' + str(6 - len(menus))