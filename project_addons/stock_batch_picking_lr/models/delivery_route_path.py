# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class DeliveryRoutePath(models.Model):
    _name = 'delivery.route.path'
    _order = 'name ASC'

    name = fields.Char('Route name')