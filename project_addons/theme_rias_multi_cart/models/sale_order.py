# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api
from pprint import pprint

class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def get_product_qty(product_id):
        pprint(product_id)
        line_obj = self.website_order_line.search([('product_id', '=', product_id)])
        pprint(line_obj)
        pprint(line_obj.product_uom_qty)
        return line_obj.product_uom_qty
