# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    no_group_invoices = fields.Boolean(
        string='No Group assigned invoices',
        default=True,
    )
