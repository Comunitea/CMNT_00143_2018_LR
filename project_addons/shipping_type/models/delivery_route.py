# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryPartnerOrder(models.Model):

    _name = "route.partner.order"

    route_id = fields.Many2one('delivery.route.path')
    sequence = fields.Integer('Orden en ruta', default=10)
    partner_id = fields.Many2one('res.partner', 'Cliente', domain=[('customer', '=', True)])


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
    partner_order_ids = fields.One2many('route.partner.order', 'route_id')