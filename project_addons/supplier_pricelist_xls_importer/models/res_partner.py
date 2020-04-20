# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    discount_groups = fields.One2many('supplier.discount.group', 'partner_id')
