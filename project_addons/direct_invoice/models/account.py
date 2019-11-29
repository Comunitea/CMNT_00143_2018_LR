# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'



class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    def create_direct_invoice_ids(self, imported_vals):

        # de los valores importados
        return
        



class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

