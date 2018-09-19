# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class AccountAnalyticAccount(models.Model):

    _inherit= 'account.analytic.account'

    recurring_rule_type = fields.Selection(selection_add=[('monthlyfirstday', 'Month(s) first day'),])

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        res = super(AccountAnalyticAccount, self).get_relative_delta(recurring_rule_type, interval)
        if recurring_rule_type == 'monthlyfirstday':
            return relativedelta(months=interval, day=1)
        return res

