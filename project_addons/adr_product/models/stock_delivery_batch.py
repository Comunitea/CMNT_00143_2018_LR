# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockBatchDelivery(models.Model):
    _inherit = 'stock.batch.delivery'

    @api.multi
    def print_rda_delivery(self):
        self.ensure_one()
        move_ids = self.env['stock.move'].search([('batch_delivery_id', '=', self.id)]).filtered(lambda x: x.quantity_done >0)
        if not move_ids:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return {'type': 'ir.actions.report','report_name': 'adr_product.batch_delivery_adr_view','report_type':"qweb-pdf",'data': None, 'docids' : active_ids}

    @api.multi
    def action_confirm(self):
        res = super(StockBatchDelivery, self).action_confirm()
        if self._check_if_can_be_shipped() == True:
            return res
    
    def _check_if_can_be_shipped(self):
        for delivery_batch in self:
            move_lines = delivery_batch.move_lines.filtered(lambda x: x.product_uom_qty != 0.00 and x.product_tmpl_id.adr_idnumonu)

            if not move_lines:
                return True
                raise ValidationError(_("There are no ADR products in this delivery batch."))

            move_line_ids = self.env['stock.move.line'].search([('move_id', 'in', move_lines.ids)])
            
            weight = delivery_batch._get_weight_data(move_line_ids)

            if weight >= 1000:
                raise ValidationError(_("The weight it's over 1000 kgs. You may need to split the cargo."))
            else:
                return True

    def _get_weight_data(self, move_line_ids):
        move_line_ids = move_line_ids.filtered(lambda x: not x.product_id.product_tmpl_id.adr_exe22315 and\
                not x.product_id.product_tmpl_id.adr_idnumonu.qty_limit >= x.product_id.product_tmpl_id.weight)

        products = move_line_ids.mapped('product_id')
        categories = products.mapped('product_tmpl_id').mapped('adr_idnumonu').mapped('adr_category_id')

        weight = 0.0

        if len(categories) > 1:
            for line in move_line_ids:
                weight += line.product_id.product_tmpl_id.adr_weight_x_kgrs_11363*line.product_uom_qty
        else:
            for line in move_line_ids:
                weight += line.product_id.product_tmpl_id.adr_weight_x_kgrs_11364*line.product_uom_qty

        return weight
        

        