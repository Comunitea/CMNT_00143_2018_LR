# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    fair_id = new_field = fields.Many2one('virtual.fair', 'Virtual Fair')
    digit_date = fields.Date('Digit Date')
    num_ass = fields.Char('Num Associated')
    num_conf = fields.Char('Conformation number')
    featured = fields.Boolean('Featured')
