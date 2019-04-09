# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint

class DeliveryBatchCustomReport(models.AbstractModel):

    _name = 'report.stock_delivery_batch.delivery_batch_view'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = data['docs']
        
        origin = data['form']['origin']
        delivery_carrier_data = data['form']['delivery_carrier_data']
        exention_type = data['form']['exention_type']
        category_max_weight = data['form']['category_max_weight']
        regular_total_weight = data['form']['regular_total_weight']
        exe22315_total_weight = data['form']['exe22315_total_weight']
        lq_total_weight = data['form']['lq_total_weight']
        counter_22315 = data['form']['counter_22315']
        counter_lq = data['form']['counter_lq']
        company_data = data['form']['company_data']
        picking_batch = data['form']['picking_batch']
        delivery_date = data['form']['delivery_date']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'origin': origin,
            'exention_type': exention_type,
            'delivery_carrier_data': delivery_carrier_data,
            'category_max_weight': category_max_weight,
            'regular_total_weight': regular_total_weight,
            'exe22315_total_weight': exe22315_total_weight,
            'lq_total_weight': lq_total_weight,
            'counter_22315': counter_22315,
            'counter_lq': counter_lq,
            'company_data': company_data,
            'picking_batch': picking_batch,
            'delivery_date': delivery_date,
            'docs': docs
        }