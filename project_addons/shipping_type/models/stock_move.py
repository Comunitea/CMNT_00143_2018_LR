# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


class StockMoveLine(models.Model):

    _inherit = ['stock.move.line', 'info.route.mixin']
    _name = 'stock.move.line'

    delivery_route_path_id = fields.Many2one(related="move_id.delivery_route_path_id")
    shipping_type = fields.Selection(related="move_id.shipping_type")
    campaign_id = fields.Many2one(related="move_id.campaign_id")

    @api.model
    def create(self, vals):
        return super().create(vals)


    @api.multi
    def write(self, vals):
        return super().write(vals)

    def update_to_new_package(self, new_package_ids):
        ## revisar esto
        create = True
        for pack in new_package_ids:
            ok = pack.update_info_route_vals() == self.update_info_route_vals()
            if ok:
                self.move_id.write({'result_package_id': pack.id})
                create = False
                break
        if create:
            vals_0 = self.update_info_route_vals()
            new_result_package_id = pack.create(vals_0)
            self.move_id.write({'result_package_id': new_result_package_id.id})
            new_package_ids += new_result_package_id
        return new_package_ids


class StockMove(models.Model):
    _inherit = ['stock.move', 'info.route.mixin']
    _name = 'stock.move'

    #carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    carrier_id = fields.Many2one(related="picking_id.carrier_id", string="Carrier")
    delivery_route_path_id = fields.Many2one(related="picking_id.delivery_route_path_id", store=True)
    shipping_type = fields.Selection(related="picking_id.shipping_type", store=True)
    payment_term_id = fields.Many2one(related="picking_id.payment_term_id", store=True)

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id:
            vals.update(self.sale_line_id.order_id.update_info_route_vals())
        return vals

    def _get_new_picking_domain(self):
        return super()._get_new_picking_domain()

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update(self.update_info_route_vals())
        return res

    def _prepare_extra_move_vals(self, qty):
        res = super()._prepare_extra_move_vals(qty=qty)
        res.update(self.update_info_route_vals())
        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty=qty)
        res.update(self.update_info_route_vals())
        return res

    @api.multi
    def write(self, vals):
        return super().write(vals)