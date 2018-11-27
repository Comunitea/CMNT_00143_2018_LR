# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    def draft2open(self):
        clean_journal = self.env['account.payment.order']
        for order in self:
            if not order.journal_id:
                order.journal_id = order.payment_mode_id.variable_journal_ids \
                    and order.payment_mode_id.variable_journal_ids[0] or \
                    order.payment_mode_id.fixed_journal_id
                clean_journal += order
        res = super(AccountPaymentOrder, self).draft2open()
        if clean_journal:
            clean_journal.write({'journal_id': False})
        return res

    def action_view_payment_line(self):
        action = self.env.ref(
            'account_payment_order.bank_payment_line_action').read()[0]
        action['domain'] = [('id', 'in', self.bank_line_ids._ids)]
        return action

    def split_order(self):
        orders = self
        order_key = (self.journal_id.id, self.payment_mode_id.id)
        grouped_lines = {}
        for line in self.bank_line_ids:
            group_key = line.get_group_key()
            if group_key == order_key:
                continue
            if group_key not in grouped_lines.keys():
                grouped_lines[group_key] = line
            else:
                grouped_lines[group_key] += line
        for key in grouped_lines.keys():
            journal_id = key[0]
            payment_mode_id = key[1]
            new_order = self.copy(
                {'payment_mode_id': payment_mode_id, 'journal_id': journal_id})
            grouped_lines[key].mapped('payment_line_ids').write(
                {'order_id': new_order.id})
            grouped_lines[key].write(
                {'order_id': new_order.id})
            new_order.state = 'open'
            orders += new_order
        action = self.env.ref(
            'account_payment_order.account_payment_order_inbound_action').read(
            )[0]
        action['domain'] = [('id', 'in', orders._ids)]
        return action
