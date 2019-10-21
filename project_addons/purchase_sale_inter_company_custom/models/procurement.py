# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, api, models

class ProcurementRule(models.Model):
    _inherit = "procurement.rule"


    def _prepare_purchase_order(self, product_id, product_qty, product_uom,
                                origin, values, partner):
        """Propagate payment mode on MTO/drop shipping."""
        values = super(ProcurementRule, self)._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        so_origin = self.env['sale.order'].search([('name', '=', origin)], order='id desc', limit =1)
        if so_origin:
            values.update(from_sale_id=so_origin.id)
        return values

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values,
                                   group_id):
        vals = super()._get_stock_move_values(product_id=product_id,
                                                  product_qty=product_qty,
                                                  product_uom=product_uom,
                                                  location_id=location_id,
                                                  name=name,
                                                  origin=origin,
                                                  values=values,
                                                  group_id=group_id)
        sol_id = vals.get('sale_line_id', False)
        if sol_id:
            sol = self.env['sale.order.line'].browse(sol_id)
            po = sol.auto_purchase_line_id
            vals['ic_sale_line_id'] = po.sudo().move_ids.move_dest_ids.mapped('sale_line_id').id
        return vals

