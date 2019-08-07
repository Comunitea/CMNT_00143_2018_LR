# -*- coding: utf-8 -*-
# © 2018 Comunitea - Ruben Seijas <ruben@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class Website(models.Model):
    _inherit = 'website'

    def get_child_category(self, category):
        categories = self.env["product.public.category"]
        parent = category.id if category else False
        domain = [('parent_id', '=', parent), ('website_published', '=', True)]
            
        result = categories.sudo().search(domain, order='sequence')
        if len(result) < 1:
            return self.get_siblings_category(category)
        return result

    def get_siblings_category(self, category):
        categories = self.env["product.public.category"]
        if not category:
            return categories.sudo().search([], order='sequence')
            
        parent = category.parent_id.id if category else 0
        domain = [('parent_id', '=', parent), ('website_published', '=', True)]
        result = categories.sudo().search(domain, order='sequence')
        return result

    def latest_posts(self, qty, columns, title, read_all):
        res = super(Website, self).latest_posts(qty=qty, columns=columns,title=title,read_all=read_all)
        
        allowed_posts = []
        for post in res['posts']:
            allowed = self.access_to_blog(post.blog_id)
            
            if allowed:
                allowed_posts += post

        res['posts'] = allowed_posts
        return  res

    def category_check(self,filter=[]):
         
        if filter:
            filter.extend([('website_published','=',True)])
        else:
            filter=([('website_published','=',True)])
         
        return self.env['product.public.category'].sudo().search(filter)

    def get_submitted_pricelists(self, user_email):

        pricelist_list = self.env['crm.lead'].sudo().search([('email_from', '=', user_email)])
        attachments = self.env['ir.attachment'].sudo().search([('res_id', 'in', pricelist_list.ids),('res_model', '=', 'crm.lead')])

        data = {
            'pricelist_list': pricelist_list,
            'attachments': attachments
        }

        return data

    def crumb_for_catalogue(self, url):
        if '/shop' in url:
            return '/catalogue'
        elif '/category/' in url:
            return url.replace('/category/', '/catalogue/category/')