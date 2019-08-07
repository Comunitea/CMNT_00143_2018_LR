# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import io
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
from pprint import pprint

def my_carts_control_access(order_id=False):
    
    user = request.env.user
    rules = 'b2b'

    is_b2b = user.has_group('sale.group_show_price_subtotal')
    is_b2c = user.has_group('sale.group_show_price_total')
    is_portal = user.has_group('base.group_portal')
    is_admin = user.has_group('website.group_website_publisher') or user.has_group('base.group_user')

    if order_id:
        order = request.env['sale.order'].sudo().browse([order_id])
        if order.partner_id.id != user.partner_id.id:
            return request.redirect('/my')

    if not is_admin:
        # If the user is not logged in --> to login
        if not is_portal:
            path = request.httprequest.path
            query = request.httprequest.query_string
            if query:
                query = query.decode('utf-8')
                query = query.replace('&', '%26')
                path += '?%s' % query
            return request.redirect('/web/login?redirect=%s' % path)
        # If the user hasn't permission --> return error 403
        elif (rules == 'b2b' and not is_b2b) or (rules == 'b2c' and not is_b2c):
            return request.render("seo_base.403_access_to_store")
    return False

class CustomerPortalCarts(CustomerPortal):
    
    @http.route([
        '/my/carts',
    ], type='http', auth='user', website=True)
    def cart_page_access(self):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access()
            if result:
                return result

        return request.render('theme_rias_multi_cart.rias_multi_cart_my_draft_orders_view')

    @http.route([
        '/my/campaigns',
    ], type='http', auth='user', website=True)
    def campaigns_page_access(self):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access()
            if result:
                return result

        return request.render('theme_rias_multi_cart.rias_multi_cart_my_campaigns_view')

    @http.route([
        '/my/campaigns/select/<int:campaign>',
    ], type='http', auth='user', website=True)
    def set_active_campaign(self, campaign=None, **post):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access()
            if result:
                return result

        sale_order = request.website.get_campaign_cart(campaign)
        if sale_order:
            return request.redirect('/shop')
    
    @http.route([
        '/my/carts/<int:order>',
    ], type='http', auth='user', website=True)
    def portal_cart_page(self, order=None, access_token=None, **post):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access(order)
            if result:
                return result

        order = request.env['sale.order'].browse([order])
        order_sudo = order.sudo()

        values = self._order_get_page_view_values(order_sudo, access_token, **post)
        return request.render("sale.portal_order_page", values)

    @http.route([
        '/my/carts/select/<int:order>',
    ], type='http', auth='user', website=True)
    def set_active_cart(self, order=None, **post):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access(order)
            if result:
                return result

        sale_order = request.website.get_selected_cart(order)
        if sale_order:
            return request.redirect('/shop')
    
    @http.route([
        '/my/carts/new',
    ], type='http', auth='user', website=True)
    def create_new_cart(self, user=None, **post):

        # Call to the user access control function
        if request.website:
            result = my_carts_control_access()
            if result:
                return result

        sale_order = request.website.get_new_cart()
        if sale_order:
            return request.redirect('/shop')

    @http.route(['/shop/cart/is_allowed_purchase_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def is_allowed_purchase_json(self, product_id):
        res = request.website.is_allowed_purchase(product_id)
        return res

    #@http.route(['/shop/cart/add_to_campaign_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    #def add_to_campaign_json(self, product_id, campaign_id, line_id=None, add_qty=None, set_qty=None, display=True):
    #    pprint(campaign_id)
    #    pprint(product_id)
    #    order = request.website.sudo().get_campaign_cart(campaign_id)
    #    pprint(order)
    #    if order.state != 'draft':
    #        pprint("reset")
    #        request.website.sale_reset()
    #        return request.redirect('/shop')
    #    value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
    #
    #    if not order.cart_quantity:
    #        request.website.sale_reset()
    #        return request.redirect('/shop')
    #    
    #    return request.redirect('/shop')

class WebsiteSaleContext(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, check_campaign=True):

        res = super(WebsiteSaleContext, self)._get_search_domain(search=search, category=category, attrib_values=attrib_values)
        if check_campaign:
            cart = request.website.sale_get_order()
            if cart.campaign_id:
                campaign_products = cart.campaign_id.article_ids.mapped('product_id').ids
                campaign_products_tmpl = cart.campaign_id.article_ids.mapped('product_id').mapped('product_tmpl_id').ids
                res += ['|',('id', 'in', campaign_products_tmpl),('product_variant_ids', 'in', campaign_products)]
        return res