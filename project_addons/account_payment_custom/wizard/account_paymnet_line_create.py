# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'
    _description = 'Wizard to create payment lines'

    start_due_date = fields.Date(string="Start Due Date")
