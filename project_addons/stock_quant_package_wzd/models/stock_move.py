# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self.move_line_ids.mapped('result_package_id'):
            batch_delivery_id = self.move_line_ids.mapped('result_package_id')
            domain += [('batch_delivery_id', '=', batch_delivery_id.id)]
        return domain
