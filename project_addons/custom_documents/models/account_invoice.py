# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):

    _name = 'account.invoice'
    _inherit = [_name, "base_multi_image.owner"]
