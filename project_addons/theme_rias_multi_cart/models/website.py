# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api
from odoo.http import request
from pprint import pprint

class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_selected_cart(self, sale_order_id):
        self.ensure_one()
        sale_order = self.env['sale.order'].browse(sale_order_id)
        if sale_order:
            request.session['sale_order_id'] = sale_order.id
            pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id
            request.session['website_sale_current_pl'] = pricelist_id
        else:
            request.session['sale_order_id'] = None
            request.session['website_sale_current_pl'] = None
            raise ValueError(
                    'We could not find the order with ID: %s, '
                    'please check if the order is already processed.'
                    % sale_order_id)
        return sale_order
    
    @api.multi
    def get_user_draft_carts(self):
        self.ensure_one()
        user_id = self.env.user.partner_id.id
        if user_id:
            sale_orders = self.env['sale.order'].search([('partner_id', '=', user_id), ('state', '=', 'draft')])
        else:
            raise ValueError(
                    'We found a problem with your user, '
                    'try login again or contact an admin.')
        return sale_orders

    @api.multi
    def get_new_cart(self):
        partner = request.website.partner_id
        pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id
        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
        so_data = self._prepare_sale_order_values(partner, pricelist)
        sale_order = self.env['sale.order'].with_context(force_company=request.website.company_id.id).sudo().create(so_data)

        # set fiscal position
        if request.website.partner_id.id != partner.id:
            sale_order.onchange_partner_shipping_id()
        else: # For public user, fiscal position based on geolocation
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                fp_id = request.env['account.fiscal.position'].sudo().with_context(force_company=request.website.company_id.id)._get_fpos_by_region(country_id)
                sale_order.fiscal_position_id = fp_id
            else:
                # if no geolocation, use the public user fp
                sale_order.onchange_partner_shipping_id()

        request.session['sale_order_id'] = sale_order.id

        if request.website.partner_id.id != partner.id:
            partner.write({'last_website_so_id': sale_order.id})
        

        if sale_order:
            # case when user emptied the cart
            if not request.session.get('sale_order_id'):
                request.session['sale_order_id'] = sale_order.id

            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id.id

                # change the partner, and trigger the onchange
                sale_order.write({'partner_id': partner.id})
                sale_order.onchange_partner_id()
                sale_order.onchange_partner_shipping_id() # fiscal position
                sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True

                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order.write(values)

                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id.id
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True
            return sale_order
        else:
            request.session['sale_order_id'] = None
            return self.env['sale.order']

    @api.multi
    def get_current_cart_qty(self, website_sale_order, product_id, variant=False):

        if variant == False:
            line = website_sale_order.website_order_line.search([('product_tmpl_id', '=', product_id), ('order_id', '=', website_sale_order.id)])
        else:
            line = website_sale_order.website_order_line.search([('product_id', '=', product_id), ('order_id', '=', website_sale_order.id)])
        
        product_line_data = {
            'line_id': line.id,
            'product_uom_qty': line.product_uom_qty,
        }
        
        return product_line_data

    @api.multi
    def get_products_in_cart(self, website_sale_order):
        products_ids = website_sale_order.website_order_line.mapped('product_id').ids
        product_tmpl_ids = self.env['product.product'].browse(products_ids).mapped('product_tmpl_id').ids        
        return product_tmpl_ids

    @api.multi
    def check_user_group(self):
        if self.env.user.has_group('sale.group_show_price_subtotal'):
            return True
        else:
            return False
