# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PaymentReturn(models.Model):
    _inherit = 'payment.return'

    def action_confirm(self):
        res = super(PaymentReturn, self).action_confirm()
        self.mapped(
            'line_ids.move_line_ids.matched_debit_ids.origin_returned_move_ids'
            ).write({'blocked': True})
        return res
