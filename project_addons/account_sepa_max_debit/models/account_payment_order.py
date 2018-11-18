# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountPaymentOrder(models.Model):

    _inherit = 'account.payment.order'

    ignored_payment_line_ids = fields.One2many(
        'account.payment.line', 'order_id2',
        string='Transaction Lines Ignored',
        readonly=True)

    @api.multi
    def draft2open(self):
        """
        Ignore payment lines if it raises the partner sepa_max_debit
        field, in the customers form.
        """
        res = super(AccountPaymentOrder, self).draft2open()
        self.ignore_lines_raising_limit()
        return res

    @api.multi
    def action_cancel(self):
        """
        Delete the ignored transitions when cancel.
        """
        res = super(AccountPaymentOrder, self).action_cancel()
        for order in self:
            order.ignored_payment_line_ids.unlink()
        return res

    @api.model
    def remove_raising_transitions(self, bline, limit):
        """
        Remove from the bank payment line, the payment lines raising the limit
        and put it into new ignored_transitions_field
        """
        pline2remove = self.env['account.payment.line']

        total = 0.0
        # Get payment lines thar raises the partner limit
        for pline in bline.payment_line_ids:
            total += pline.amount_currency
            if total > limit:
                pline2remove += pline

        if pline2remove:
            # Unlink from transitions and sedt in ignored transitions field
            pline2remove.write({
                'order_id': False,
                'order_id2': self.id,
                'bank_line_id': False
            })
            # Remove bank payment line if no payment_line_ids linked
            if not bline.payment_line_ids:
                bline.unlink()

    @api.multi
    def ignore_lines_raising_limit(self):
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
            # self._recursive_ungroup_line(bline, limit)
            self.remove_raising_transitions(bline, limit)


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    order_id2 = fields.Many2one(
        'account.payment.order', string='Payment Order',
        ondelete='cascade', index=True)
