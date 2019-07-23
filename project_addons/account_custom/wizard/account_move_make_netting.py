# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMoveMakeNetting(models.TransientModel):
    _inherit = "account.move.make.netting"

    def button_compensate(self):
        res = super().button_compensate()
        partner = self.move_line_ids.mapped('partner_id')
        template = self.env.ref('account_custom.netting_advice_mailing_template', False)
        ctx = dict(self._context)
        ctx.update({
            'partner_email': partner.email,
            'partner_id': partner.id,
            'partner_name': partner.name,
            'moves': self.move_line_ids,
            'obj': partner,
        })
        mail_id = template.with_context(ctx).send_mail(partner.id)
        self.env['mail.mail'].browse(mail_id).send()
        return res
