# © 2018 Comunitea
# License AGPL-3
from odoo import _, api, fields, exceptions, models


class StockLocation(models.Model):

    _inherit ="stock.location"

    check_availability = fields.Boolean("Check availability", help="If checked, all moves waiting availability with this origin are check in background")