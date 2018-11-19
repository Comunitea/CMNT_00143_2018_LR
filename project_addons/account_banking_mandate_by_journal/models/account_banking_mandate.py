# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountBankingMandate(models.Model):
    _inherit = 'account.banking.mandate'

    journal_ids = fields.Many2many('account.journal', string='journals')
