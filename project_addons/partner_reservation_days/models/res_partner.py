# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    reservation_days = fields.Integer (string="Reservation days", default=0, help="Days to calculate when sale order lines are cancelled")


