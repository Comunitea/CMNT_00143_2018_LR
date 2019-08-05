# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProductProduct(models.Model):

    _inherit = 'product.product'

    abc_classification = fields.Selection([
            ('A', 'A'),
            ('A1', 'A1'),
            ('A2', 'A2'),
            ('B', 'B'),
            ('B1', 'B1'),
            ('C', 'C'),
            ('C1', 'C1'),
            ('C2', 'C2'),
            ('no', 'None'),
        ], 'ABC Classification', default='no')

    force_abc = fields.Boolean('Force Classification')

    def _get_sale_months(self, month_picks, history_line):
        sale_months = 0

        months_set = set([x['date_done'] for x in month_picks])
        history_set = set()

        # Cálculo el mes a partir del cual ya no miro el histórico
        # que sería el mes anterior a un año atrás
        year_ago_date = (datetime.now() - relativedelta(months=13))
        limit_year = str(year_ago_date.year)
        limit_month_name = year_ago_date.strftime('%B')
        limit_complete_month_name = limit_month_name + ' ' + limit_year

        if history_line:
            month_fields = [
                'month_1', 'month_2', 'month_3', 'month_4', 'month_5',
                'month_6', 'month_7', 'month_8', 'month_9', 'month_10',
                'month_11', 'month_12'
            ]
            for m in month_fields:
                if not eval('history_line.' + m):
                    continue
                num = int(m.split('_')[1])
                date_file = datetime.strptime(history_line.date, '%Y-%m-%d')
                date_sale = date_file - relativedelta(months=num)
                num_year = str(date_sale.year)
                month_name = date_sale.strftime('%B')
                complete_month_name = month_name + ' ' + num_year

                # Si ya ha pasado un año desde el momento actual, 
                # no sigo consultandfo el histórico
                if complete_month_name == limit_complete_month_name:
                    break

                history_set.add(complete_month_name)

        sale_months = len(months_set | history_set)
        return sale_months

    @api.model
    def get_classification(self, sale_months, product):
        sm = self.env['stock.move']
        res = 'no'
        ranges_ab = {
            (11, 12): 'A',
            (8, 10): 'A1',
            (6, 7): 'A2',
            (4, 5): 'B',
            (1, 3): 'B1',
        }
        for ran in ranges_ab:
            ini = ran[0]
            end = ran[1] + 1
            if sale_months in range(ini, end):
                res = ranges_ab[ran[0], ran[1]]
                break

        current_date = datetime.now().strftime('%Y-%m-%d')
        month3_ago_date = \
            (datetime.now() - relativedelta(month=3)).strftime('%Y-%m-%d')

        if sale_months == 0:
            res = 'C'
            if product.create_date >= month3_ago_date:
                res = 'C2'

        if res == 'B1':
            domain = [
                ('product_id', '=', product.id),
                ('picking_id.date_done', '>=', month3_ago_date),
                ('picking_id.date_done', '<=', current_date),
                ('picking_id.state', 'in', ['done'])
            ]
            moves = sm.search(domain)
            if not moves:
                res = 'C1'
        return res

    @api.multi
    def compute_abc_classification(self):
        sm = self.env['stock.move']
        current_date = datetime.now().strftime('%Y-%m-01')
        year_ago_date = \
            (datetime.now() - relativedelta(months=12)).strftime('%Y-%m-01')
        for product in self.filtered(lambda p: not p.force_abc):
            product.abc_classification = 'no'

            # Busco un año atrás sin incluir el principiop del mes actual
            # cogiendo los días 01 de cada mes
            domain = [
                ('product_id', '=', product.id),
                ('picking_id.date_done', '>=', year_ago_date),
                ('picking_id.date_done', '<', current_date),
                ('picking_id.state', 'in', ['done'])
            ]
            moves = sm.search(domain)
            month_picks = moves.mapped('picking_id').read_group(
                [('date_done', '!=', False)], 
                ['name', 'date_done'], ['date_done'])

            history_line = self.env['stock.rotation.history'].search(
                [('product_id', '=', product.id)], limit=1)
            sale_months = self._get_sale_months(month_picks, history_line)
            product.abc_classification = self.get_classification(sale_months,
                                                                 product)

    @api.model
    def cron_compute_abc_classification(self):
        self.env['product.product'].search([]).compute_abc_classification()
