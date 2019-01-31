# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from functools import partial
from odoo import api, fields, models
from odoo.tools.misc import formatLang


class AccountInvoice(models.Model):

    _name = 'account.invoice'
    _inherit = [_name, "base_multi_image.owner"]


    @api.multi
    def _get_tax_amount_by_group_signed(self):
        sign = 1
        if 'refund' in self.type:
            sign = -1
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        fmt = partial(
            formatLang,
            self.with_context(lang=self.partner_id.lang).env,
            currency_obj=currency)
        res = {}
        for line in self.tax_line_ids:
            res.setdefault(line.tax_id.tax_group_id,
                           {'base': 0.0, 'amount': 0.0})
            res[line.tax_id.tax_group_id]['amount'] += sign * line.amount_total
            res[line.tax_id.tax_group_id]['base'] += sign * line.base
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(
            r[0].name, r[1]['amount'], r[1]['base'],
            fmt(r[1]['amount']), fmt(r[1]['base']),
        ) for r in res]
        return res


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    price_unit_signed = fields.Float(compute='_compute_price_unit_signed')

    def _compute_price_unit_signed(self):
        for invoice_line in self:
            sign = 1
            if 'refund' in invoice_line.invoice_id.type:
                sign = -1
            invoice_line.price_unit_signed = invoice_line.price_unit * sign
