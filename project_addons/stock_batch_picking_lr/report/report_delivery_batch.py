# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint

class DeliveryBatchReport(models.AbstractModel):

    _name = 'report.stock_batch_picking_lr.delivery_batch_view'

    def get_report_values(self, docids, data=None):

        docids = docids or self.env.context.get('active_ids')
        model = self.env.context.get('active_model', 'stock.batch.picking')
        objects = self.env[model].browse(docids)
        pickings = self.env.context.get('pickings') or self.env['stock.picking'].search([('batch_picking_id', '=', docids)])
        
        company_data = {
            'logo_web': objects[0].picker_id.company_id.logo_web,
            'company_name': objects[0].picker_id.company_id.name,
            'street': objects[0].picker_id.company_id.street,
            'street2': objects[0].picker_id.company_id.street2,
            'zip': objects[0].picker_id.company_id.zip,
            'city': objects[0].picker_id.company_id.city,
            'state_id': objects[0].picker_id.company_id.state_id.name,
            'country_id': objects[0].picker_id.company_id.country_id.name,
            'vat': objects[0].picker_id.company_id.vat
        }

        delivery_carrier_data = {
            'name': objects[0].carrier_partner_id.name,
            'street': objects[0].carrier_partner_id.street,
            'street2': objects[0].carrier_partner_id.street2,
            'zip': objects[0].carrier_partner_id.zip,
            'city': objects[0].carrier_partner_id.city,
            'state_id': objects[0].carrier_partner_id.state_id.name,
            'country_id': objects[0].carrier_partner_id.country_id.name,
            'vat': objects[0].carrier_partner_id.vat,
            'vehicle': objects[0].carrier_partner_id.vehicle_plates
        }

        elements = []
        partners_data = []
        partners_index = []
        partner_pickings = []

        for pick in pickings:
            
            for line in pick.move_line_ids:

                product_tmpl_line = line.product_id.product_tmpl_id
                move_line = line.move_id

                ## Metemos el id en partners para tener un listado de los destinatarios. 
                if not move_line.partner_id.id in partners_index:
                    partners_index.append(move_line.partner_id.id)
                    partners_data.append({
                        'id': move_line.partner_id.id,
                        'name': move_line.partner_id.name
                    })

                partner_pickings.append({
                    'partner_id': move_line.partner_id.id,
                    'line_id': line.id,
                    'origin': move_line.origin,
                    'name': product_tmpl_line.name,
                    'default_code': product_tmpl_line.default_code,
                    'product_qty': line.qty_done,
                    'picking_id': line.picking_id.name,
                    'result_package_id': line.result_package_id.name
                })

        elements.append({
            'partners': partners_data,
            'movements': partner_pickings
        })

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'docs': objects,
            'elements': elements,
            'company_data': company_data,
            'delivery_carrier_data': delivery_carrier_data,
            'pickings': pickings
        }
        return docargs