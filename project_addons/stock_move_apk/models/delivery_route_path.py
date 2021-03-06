# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class DeliveryRoutePath(models.Model):
    _inherit = 'delivery.route.path'



    def get_path_route_domain(self):

        return []

    @api.model
    def get_routes_for_apk(self, vals):
        routes = self.search(self.get_path_route_domain())
        apk_routes = []
        for route in routes:
            apk_routes.append({
                'id': route.id,
                'name': route.name
            })
        return apk_routes