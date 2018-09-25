# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountPaymentOrder(models.Model):

    _inherit = 'account.payment.order'

    @api.multi
    def draft2open(self):
        """
        Ungroup bank payment lines if it raises the partner  sepa_max_debit
        field, in the customers form.
        """
        res = super(AccountPaymentOrder, self).draft2open()
        self.ungroup_bank_payment_lines()
        return res

    @api.model
    def _recursive_ungroup_line(self, bline, limit):
        """
        Create more lines whitch no limit rebased
        """
        pline2split = self.env['account.payment.line']

        total = 0.0
        # Get payment lines thar raises the partner limit
        for pline in bline.payment_line_ids:
            total += pline.amount_currency
            if total > limit:
                pline2split += pline

        # When no pline2split we are in base case of recursive funcion
        if pline2split:
            # Creating new bank payment line
            new_name = self.env['ir.sequence'].\
                next_by_code('bank.payment.line') or 'New'
            default = {
                'name': new_name,
                'communication': '-'.join(
                    [line.communication for line in pline2split])
            }
            new_bline = bline.copy(default)

            # Linking lines 2 split to the new bank payment line
            pline2split.write({'bank_line_id': new_bline.id})

            # Update communication with only the payment lines linked to it
            bline.write({'communication': '-'.join(
                [line.communication for line in bline.payment_line_ids])})

            # Call for the new bline, until new_line dont raises the limit
            self._recursive_ungroup_line(new_bline, limit)

    @api.multi
    def ungroup_bank_payment_lines(self):
        """
        For each line, if partner limit is raised, we create new bank lines
        above the partner limit.
        """
        for bline in self.bank_line_ids:
            limit = bline.partner_id.sepa_max_debit
            if not limit:  # Skip if no limit setted.
                continue
            if limit > bline.amount_currency:  # Skip if no limit raised
                continue
            self._recursive_ungroup_line(bline, limit)
