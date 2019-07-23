# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    route_ids = fields.Many2many('delivery.route.path', string="Routes")


class DeliveryRoutePathDay(models.Model):

    _name = "delivery.route.path.day"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Day')


class DeliveryRoutePath(models.Model):
    _name = 'delivery.route.path'
    _order = 'name ASC'

    name = fields.Char('Route code')
    description = fields.Char("Description")
    day_ids = fields.Many2many('delivery.route.path.day')


