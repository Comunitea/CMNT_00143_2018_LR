# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticContract(models.Model):
    _inherit = 'account.analytic.contract'

    recurring_payment_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic payment order generation.",
    )
    recurring_payment_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )

    recurring_voucher_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic payment order generation.",
    )
    recurring_voucher_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )
