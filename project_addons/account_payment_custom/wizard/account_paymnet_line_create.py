# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'
    _description = 'Wizard to create payment lines'

    start_due_date = fields.Date(string="Start Due Date")

    @api.multi
    def _prepare_move_line_domain(self):
        domain = super(AccountPaymentLineCreate, self).\
            _prepare_move_line_domain()
        if ('date_maturity', '=', False) in domain and self.start_due_date:
            indx = domain.index(('date_maturity', '=', False)) + 1
            t = ('date_maturity', '>=', self.start_due_date)
            domain.insert(indx, t)
        return domain
