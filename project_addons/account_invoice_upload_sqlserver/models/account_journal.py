# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sqlserver_id = fields.Integer()
