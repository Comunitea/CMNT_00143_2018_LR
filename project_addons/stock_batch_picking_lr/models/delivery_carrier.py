# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    partner_ids = fields.One2many('res.partner', 'delivery_id', string="Carrier Drivers", copy=True)