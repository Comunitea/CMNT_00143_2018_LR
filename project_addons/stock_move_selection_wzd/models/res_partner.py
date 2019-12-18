# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    route_driver = fields.Boolean('Route driver')

    def get_route_order(self, delivery_route_path_id):

        return 1