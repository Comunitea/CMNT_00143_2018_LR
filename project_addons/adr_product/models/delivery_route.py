# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryRoutePath(models.Model):
    _inherit = 'delivery.route.path'

    partner_ids = fields.One2many('res.partner', 'delivery_route_path_id')