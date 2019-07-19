# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import io
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal

class CustomerPortalCarts(CustomerPortal):
    
    @http.route([
        '/my/carts/<int:order>',
    ], type='http', auth='user', website=True)
    def portal_order_page(self, order=None, **post):
        response = super(CustomerPortalCarts, self).portal_order_page(order=order, **post)
        return response

    @http.route([
        '/my/carts/select/<int:order>',
    ], type='http', auth='user', website=True)
    def set_active_cart(self, order=None, **post):
        sale_order = request.website.get_selected_cart(order)
        if sale_order:
            return request.redirect('/shop')
    
    @http.route([
        '/my/carts/new',
    ], type='http', auth='user', website=True)
    def create_new_cart(self, user=None, **post):
        sale_order = request.website.get_new_cart()
        if sale_order:
            return request.redirect('/shop')