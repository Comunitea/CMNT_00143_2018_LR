# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import http, api, models, fields, _

from odoo.http import request
from pprint import pprint

class Menu(models.Model):

    _inherit = "website.menu"

    menu_icon = fields.Char('Icon', default='', help='You can check the full list of icons at https://fontawesome.com/cheatsheet?from=io')
    for_retailers = fields.Boolean(string=_("Available for B2B users"), default=True)
    for_customers = fields.Boolean(string=_("Available for B2C users"), default=True)
    website_published = fields.Boolean(string='Published', default=True)
    dynamic_cat_menu = fields.Boolean(string='Dynamic categories menu', default=False)
    top_menu_retailers = fields.Boolean(string="Available on top menu", default=False)


class WebsiteBlog(models.Model):
    _inherit = 'website'

    def dynamic_category_list(self):
        domain = []
        return self.env['product.public.category'].sudo().search(domain)

    @api.multi
    def allowed_menus(self, menus):
        allowed_menus = []
        for menu in menus.filtered(lambda a: a.website_published and a.menu_icon):
            user = request.env.user

            user_b2b = user.has_group('sale.group_show_price_subtotal')
            user_b2c = user.has_group('sale.group_show_price_total') or user.has_group('base.group_public')
            user_admin = user.has_group('website.group_website_publisher') or user.has_group('base.group_user')

            if (menu.for_retailers and user_b2b) or (menu.for_customers and user_b2c) or user_admin:
                allowed_menus += menu
        
        return allowed_menus

    @api.multi
    def calculate_offset(self, menus):
        if len(menus) < 6:
            return 'col-md-offset-' + str(6 - len(menus))
