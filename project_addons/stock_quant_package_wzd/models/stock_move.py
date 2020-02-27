# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self._context.get('result_package_id', False):
            package = self.env['stock.quant.package'].browse(self._context['result_package_id'])
            vals.update(package.update_info_route_vals())
        return vals

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self._context.get('result_package_id', False):
            package = self.env['stock.quant.package'].browse(self._context['result_package_id'])
            if package.delivery_route_path_id:
                domain += [('result_package_id', '=', package.delivery_route_path_id.id)]
            if package.shipping_type:
                domain += [('shipping_type', '=', package.shipping_type)]
        return super()._get_new_picking_domain()

