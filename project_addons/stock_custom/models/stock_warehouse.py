# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _, api


class SaleOrderLine(models.Model):

    _inherit = 'stock.warehouse.orderpoint'

    by_abc = fields.Boolean('By ABC classification')

    @api.multi
    def get_min_max_by_abc(self):
        """
        Recompute min and max based on abc classification
        """
        valid_abc = ['A', 'A1', 'A2']
        for op in self:
            if op.product_id.abc_classification not in valid_abc:
                continue
            min_days = 30 if op.product_id.abc_classification != 'A2' else 21
            min_op = op.product_id.get_sale_days_qty(min_days)
            max_op = op.product_id.get_sale_days_qty(60)
            if min_op or max_op:
                op.write({
                    'product_min_qty': min_op or 1,
                    'product_max_qty': max_op or min_op
                })

    @api.model
    def cron_compute_by_abc(self):
        self.search([('by_abc', '=', True)]).get_min_max_by_abc()
