# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountPaymentOrder(models.Model):

    _inherit = 'account.payment.order'

    @api.multi
    def draft2open(self):
        """
        Ignore payment lines if it raises the partner sepa_max_debit
        field, in the customers form.
        """
        res = super(AccountPaymentOrder, self).draft2open()
        self.check_lines_raising_limit()
        return res

    @api.model
    def _recursive_ungroup_line(self, bline, limit):
        """
        Create more lines whitch no limit rebased, if more than one transition
        in other case we let the limit be raising
        """
        pline2split = self.env['account.payment.line']

        total = 0.0
        # print(bline.payment_line_ids.ids)
        # Only ungroup if more than one transition
        if len(bline.payment_line_ids) > 1:
            # Get payment lines thar raises the partner limit
            for pline in bline.payment_line_ids:
                total += pline.amount_currency
                if total > limit:
                    pline2split += pline
                    total -= pline.amount_currency

        # When no pline2split we are in base case of recursive funcion
        if pline2split:
            # Si todas rebasan el límite, y son iguales que las originales,
            # dejamos solo una payment_line y hacemos la función recursiva
            # con las demás
            if bline.payment_line_ids == pline2split:
                pline2split -= pline2split[0]
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
    def check_lines_raising_limit(self):
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

            # Ungroup lines
            self._recursive_ungroup_line(bline, limit)

