# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class InvoiceMailingWzd(models.TransientModel):

    _name = 'invoice.mailing.wzd'

    @api.multi
    def send(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        grouped_invoices = self.env['account.invoice'].read_group(
            [('id', 'in', active_ids)], ['partner_id', 'date_invoice'],
            ['partner_id', 'date_invoice:day'], lazy=False)

        mail_tmp = self.env.ref('account_custom.invoices_mailing_template')
        for group in grouped_invoices:
            partner = self.env['res.partner'].browse(group['partner_id'][0])
            inv_date = group['date_invoice:day']
            mail_tmp.with_context(inv_date=inv_date).send_mail(partner.id,
                                                               True)
