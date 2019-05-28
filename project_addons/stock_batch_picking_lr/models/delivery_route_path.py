# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class DeliveryRoutePath(models.Model):
    _inherit = 'delivery.route.path'
    _order = 'name ASC'

    name = fields.Char('Route code')
    description = fields.Char("Description")
    day_ids = fields.Many2many('delivery.route.path.day')
    plate_ids = fields.Many2many('delivery.plate')


class DeliveryPlate(models.Model):
    _name = 'delivery.plate'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Plate')
    default_route_id = fields.Many2one('delivery.route.path', string="Default route")
    default_driver_id = fields.Many2one('res.partner', string="Default driver", domain=[('route_driver', '=', True)])

class DeliveryRoutePathDay(models.Model):

    _inherit = "delivery.route.path.day"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Day')
