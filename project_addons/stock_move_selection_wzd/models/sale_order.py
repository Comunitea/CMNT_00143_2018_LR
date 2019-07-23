# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_new_vals(self):

        return super().get_new_vals()
        vals.update(sga_integrated= self.shipping_type.get_sga_integrated())
        return vals