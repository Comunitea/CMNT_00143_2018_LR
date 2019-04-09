# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountPaymentMode(models.Model):

    _inherit = 'account.payment.mode'

    not_show_due_dates_in_report = fields.Boolean()
