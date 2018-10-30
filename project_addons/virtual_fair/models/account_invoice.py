# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    fair_id = new_field = fields.Many2one('virtual.fair', 'Virtual Fair')
    digit_date = fields.Date('Digit Date')
    num_ass = fields.Char('Num Associated')
    num_conf = fields.Char('Conformation number')
    featured = fields.Boolean('Featured')
    log_id = fields.Many2one('importation.log', string='Log')

    @api.multi
    def set_fair_conditions(self):
        """
        Change conditions based on virtual fair
        """
        for inv in self:
            amount = inv.amount_total
            domain = [
                ('supplier_id', '=', inv.partner_id.id),
                ('fair_id.date_start', '<=', fields.date.today()),
                ('fair_id.date_end', '>=', fields.date.today()),
            ]
            line = self.env['fair.supplier.line'].search(domain, limit=1)
            if not line:
                domain = [
                    ('date_start', '<=', fields.date.today()),
                    ('date_end', '>=', fields.date.today()),
                ]
                fair = self.env['virtual.fair'].search(domain, limit=1)
                if not fair:
                    continue
            
            fair = line.fair_id
            term_id = False
            if line.condition_type not in ['DESCUENTO_EUR', 'DESCUENTO_PCT']:
                for cond in line.condition_ids:
                    if cond.condition_type == 'PLAZO':
                        for s in cond.section_ids:
                            if amount >= s.linf and amount <= s.lsup:
                                term_id = s.term_id.id
                                break
            # TODO: Aplicar descuentos
                            
            vals = {'fair_id': fair.id}
            if term_id:
                vals.update({'payment_term_id': term_id})
            inv.write(vals)
        return
