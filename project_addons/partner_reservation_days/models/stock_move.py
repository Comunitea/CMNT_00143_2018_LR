# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class StockMove(models.Model):
    _inherit = 'stock.move'

    cancel_date = fields.Date(string='Cancel date', help="This move wil be cancelled if waiting as date")


    def get_to_cancel_domain(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        return [('state', 'in', ('waiting', 'partially_available')), ('cancel_date', '<=', today)]

    def action_cancel_auto(self):

        domain = self.get_to_cancel_domain()
        move_ids = self.sudo().env['stock.move'].search(domain)
        move_ids._action_cancel()

    def _prepare_procurement_values(self):
        values = super(StockMove, self)._prepare_procurement_values()
        if self.sale_line_id:
            values.update(sale_line_id=self.sale_line_id.id)
        return values

class ProcurementRule(models.Model):
    _inherit='procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values,
                               group_id):

        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom,
                                                                     location_id, name, origin, values, group_id)
        if values.get('sale_id'):
            sale_id = self.env['sale.order'].search_read([('id', '=', values['sale_id'])], ['reservation_days'])
            reservation_days = sale_id and sale_id[0] and sale_id[0]['reservation_days'] or 0
            if reservation_days:
                cancel_date = (fields.Datetime.from_string(result['date_expected']) + timedelta(days=reservation_days)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                result['cancel_date'] = cancel_date
                print (cancel_date)
        return result
