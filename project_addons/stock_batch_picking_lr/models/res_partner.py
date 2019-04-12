# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    delivery_id = fields.Many2one('delivery.carrier', 'Partner Carrier')
    vehicle_plates = fields.Char(string="Vehicle plates")
