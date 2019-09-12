# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
#from .res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class SaleOrder(models.Model):

    _inherit = ['sale.order', 'info.route.mixin']
    _name = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.shipping_type = self.partner_id and self.partner_id.shipping_type or False
        self.delivery_route_path_id = self.partner_id and self.partner_id.delivery_route_path_id or False
        return res

    def get_new_vals(self):
        vals = self.update_info_route_vals()
        return vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update(self.order_id.get_new_vals())
        return values