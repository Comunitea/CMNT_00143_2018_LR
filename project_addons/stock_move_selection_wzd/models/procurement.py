# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        vals = super()._get_stock_move_values(product_id=product_id,
                                              product_qty=product_qty,
                                              product_uom=product_uom,
                                              location_id=location_id,
                                              name=name,
                                              origin=origin,
                                              values=values,
                                              group_id=group_id)

        if values.get('sale_line_id', False):
            sol = self.env['sale.order.line'].browse(values['sale_line_id'])
            vals.update({'campaign_id': sol.campaign_id and sol.campaign_id.id,
                         'carrier_id': sol.order_id.carrier_id and sol.order_id.carrier_id.id,
                         })
        vals.update({'sga_integrated': self.picking_type_id.sga_integrated,
                    'sga_state': 'no_send' if self.picking_type_id.sga_integrated else 'no_integrated'})

        return vals


class PushedFlow(models.Model):
    _inherit = "stock.location.path"

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        res = super(PushedFlow, self)._prepare_move_copy_values(move_to_copy, new_date)
        if self.picking_type_id:
            res.update({'sga_integrated': self.picking_type_id.sga_integrated,
                        'sga_state': 'no_send' if self.picking_type_id.sga_integrated else 'no_integrated'})
        else:
            res.update({'sga_integrated': False,
                        'sga_state': 'no_integrated'})
        return res