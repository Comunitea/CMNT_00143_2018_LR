# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class ReportPrintBatchPicking(models.AbstractModel):
    _inherit = 'report.stock_batch_picking.report_batch_picking'

    @api.model
    def _get_grouped_data(self, batch):
        grouped_data = {}
        for picking in batch.picking_ids:
            if picking.sale_id not in grouped_data:
                grouped_data[picking.sale_id] = self.env['stock.move.line']
            grouped_data[picking.sale_id] += picking.move_line_ids
        return grouped_data

    # @api.model
    # def get_report_values(self, docids, data=None):
    #     model = 'stock.batch.picking'
    #     docs = self.env[model].browse(docids)
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': model,
    #         'data': data,
    #         'docs': docs,
    #         'get_grouped_data': self._get_grouped_data,
    #         'now': fields.Datetime.now,
    #     }
