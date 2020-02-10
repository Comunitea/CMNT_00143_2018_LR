# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import io
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_form.controllers.main import WebsiteForm
import json
from pprint import pprint


PPG = 20
PPR = 4

def pricelist_control_access():
    
    user = request.env.user
    rules = 'b2b'

    is_b2b = user.has_group('sale.group_show_price_subtotal')
    is_b2c = user.has_group('sale.group_show_price_total')
    is_portal = user.has_group('base.group_portal')
    is_admin = user.has_group('website.group_website_publisher') or user.has_group('base.group_user')

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

class WebsiteSaleCatalogue(WebsiteSale):

    def _get_compute_currency_and_context(self):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        return compute_currency, pricelist_context, pricelist

    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        # product attributes with at least two choices
        quantity = product._context.get('quantity') or 1
        product = product.with_context(quantity=quantity)

        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency) / quantity
            else:
                price = variant.website_public_price / quantity
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price / quantity, price])
        return attribute_value_ids

    def _get_search_order(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        return 'website_published desc,%s , id desc' % post.get('order', 'website_sequence desc')

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain

    @http.route([
        '/catalogue',
        '/catalogue/page/<int:page>',
        '/catalogue/category/<model("product.public.category"):category>',
        '/catalogue/category/<model("product.public.category"):category>/page/<int:page>',
        '/catalogue/category/<path:path>',
        '/catalogue/category/<path:path>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def catalogue(self, page=0, category=None, search='', ppg=False, path=False, **post):
        if path:
            category_list = http.request.env['product.public.category']
            category = category_list.sudo().search([('slug', '=', path)], limit=1)
             # Set new PPG from back-end settings
            if not 'ppg' in request.httprequest.args:
                IrConfigParam = request.env['ir.config_parameter']
                ppg = int(IrConfigParam.sudo().get_param('default_products_to_show', 8))
            if category:
                return self.catalogue(page=page, category=category, search=search, ppg=ppg, **post)
            else:
                return http.request.env['ir.http'].reroute('/404')

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if category:
            category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()
        
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values, check_campaign=False)

        keep = QueryURL('/catalogue', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/catalogue"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([
            ('product_ids.website_published', '=', True), 
            ('product_ids', '!=', False)
        ]).mapped('parent_id')
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            url = "/catalogue/category/%s" % slug(category)
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            selected_products = Product.search(domain, limit=False)
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }
        if category:
            values['main_object'] = category
        return request.render("theme_rias.products_catalogue", values)

    @http.route(['/catalogue/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product_catalogue(self, product, category='', search='', **kwargs):
        product_context = dict(request.env.context,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/catalogue', category=category and category.id, search=search, attrib=attrib_list)

        categs = request.env['product.public.category'].search([
            ('product_ids.website_published', '=', True), 
            ('product_ids', '!=', False)
        ]).mapped('parent_id')

        pricelist = request.website.get_current_pricelist()

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
        }
        return request.render("theme_rias.product_catalogue", values)

    @http.route('/catalogue/product/<path:path>', type='http', auth="public", website=True)
    def slug_product_catalogue(self, path, category='', search='', **kwargs):
        """
        Template render by SLUG URL and context updated by inheritance

        :return: the standard template with normal user permissions if the product exists else 404
        """

        # Call to the user access control function
        if request.website:
            result = shop_control_access(request.website)
            if result:
                return result

        prod_list = request.env['product.template']

        # Search with user permissions
        product = prod_list.search([('slug', '=', path)], limit=1)

        # Search without user permissions
        product_sudo = prod_list.sudo().search([('slug', '=', path)], limit=1)

        if product_sudo:
            self._update_context()
            return super(WebsiteSaleCatalogue, self).product_catalogue(product=product, category=category, search=search, **kwargs)
        else:
            return request.env['ir.http'].reroute('/404')

    @http.route(
        ['/pricelist/list'], type='http', auth="public", website=True)
    def pricelist_list_access(self):
        """
        Template render by SLUG URL and context updated by inheritance

        :return: the standard template with normal user permissions if the product exists else 404
        """

        # Call to the user access control function
        if request.website:
            result = pricelist_control_access()
            if result:
                return result

            return request.render('theme_rias.rias_pricelist_list_template')

    @http.route(
        ['/pricelist/form'], type='http', auth="public", website=True)
    def pricelist_form_access(self):
        """
        Template render by SLUG URL and context updated by inheritance

        :return: the standard template with normal user permissions if the product exists else 404
        """

        # Call to the user access control function
        if request.website:
            result = pricelist_control_access()
            if result:
                return result

            return request.render('theme_rias.rias_pricelist_form_template')

class WebsiteSaleFilteredCategories(WebsiteSale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSaleFilteredCategories, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        categories_in_products = request.env['product.public.category'].search([
            ('product_ids.website_published', '=', True), 
            ('product_ids', '!=', False)
        ]).mapped('parent_id')
        res.qcontext.update({
            'categories': categories_in_products
        })
        return res        

    @http.route([
        '/category/<path:path>',
        '/category/<path:path>/page/<int:page>'
    ], type='http', auth='public', website=True)
    def _shop(self, path, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSaleFilteredCategories, self)._shop(path=path, page=page, category=category, search=search, ppg=ppg, **post)
        categories_in_products = request.env['product.public.category'].search([
            ('product_ids.website_published', '=', True), 
            ('product_ids', '!=', False)
        ]).mapped('parent_id')
        res.qcontext.update({
            'categories': categories_in_products
        })
        return res     

class WebsiteForm(WebsiteForm):

    # Check and insert values from the form on the model <model>
    @http.route('/website_pricelist_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_pricelist_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps(False)

        try:
            data = self.extract_data_pricelist(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})

        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})

    # Extract all data sent by the form and sort its on several properties
    def extract_data_pricelist(self, model, values):

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
            'meta': '',         # Add metadata if enabled
        }

        authorized_fields = model.sudo()._get_form_writable_fields()
        error_fields = []


        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.rsplit('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                data['custom'] += u"%s : %s\n" % (field_name, field_value)

        # Add metadata if enabled
        environ = request.httprequest.headers.environ
        if(request.website.website_form_enable_metadata):
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP"                , environ.get("REMOTE_ADDR"),
                "USER_AGENT"        , environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"   , environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"           , environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        dest_model = request.env[model.sudo().model]
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data
