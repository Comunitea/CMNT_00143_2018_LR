# © 2020 Comunitea - Santi Argüeso <santi@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import calendar
from odoo import fields, models, api, exceptions, _
from dateutil.relativedelta import relativedelta



class CashForecast(models.Model):

    _inherit = "cash.forecast"


    def _get_cash_forecast_line_vals(self, iter, prevline_id):
        if not prevline_id:
            start_date = fields.Date.from_string(
                        self.date)
        else:
            start_date =  fields.Date.from_string(prevline_id.end_date) + \
                          relativedelta(days=+1)
        if self.period_type == 'month':
            last_month_day = calendar.monthrange(start_date.year,
                                                 start_date.month)[1]
            end_date = start_date
            end_date = end_date.replace(
                end_date.year, end_date.month, last_month_day)
        elif self.period_type == 'week':
            start_week = start_date - relativedelta(days=start_date.weekday())
            end_date = start_week + relativedelta(days=+6)
        elif self.period_type == 'day':
            end_date = start_date
        vals = super()._get_cash_forecast_line_vals(iter, prevline_id)

        loan_line_ids = self._get_loan_line(start_date, end_date)
        loan_lines =  sum(
            loan_line_ids.mapped(
            'mensualidad'))
        vals['period_balance'] += -loan_lines
        vals['final_balance'] += -loan_lines
        vals.update({
            'loan_lines': loan_lines,
            'loan_line_ids': [(6, 0, loan_line_ids.ids)],
        })
        return vals

    @api.model
    def _get_loan_line(self, date_start, date_end):
        self.ensure_one()
        loan_line_domain = [
            ('company_id', 'child_of', self.company_id.id),
            ('fecha', '<=', date_end)
        ]
        if date_start:
            loan_line_domain.append(
                ('fecha', '>=', date_start)
            )

        loan_lines = self.env['loan.line'].search(loan_line_domain)
        return loan_lines


class CashForecastLine(models.Model):

    _inherit = "cash.forecast.line"

    loan_lines = fields.Float('Loans', readonly=True, copy=False)
    loan_line_ids = fields.Many2many(
        comodel_name='loan.line', string='Loan Lines',
        relation='cash_forecast_loan_line_rel', readonly=True,
        copy=False)


    def get_calculated_loan_lines(self):
        res = self.env.ref('l10n_es_loan_manager.action_loan_line').\
            read()[0]
        res['domain'] = [('id', 'in', self.loan_line_ids.ids)]
        return res
