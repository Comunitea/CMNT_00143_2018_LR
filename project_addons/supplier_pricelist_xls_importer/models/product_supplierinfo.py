# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Productsupplierinfo(models.Model):

    _inherit = 'product.supplierinfo'

    xls_imported = fields.Boolean()
