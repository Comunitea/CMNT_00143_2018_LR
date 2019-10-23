# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint


class BatchDeliveryCustomReport(models.AbstractModel):
    _name = 'report.adr_product.batch_delivery_adr_view'

    def get_report_values(self, docids, data=None):

        partners_data = []
        partner_pickings = []
        exe11363_total_weight = 0.0
        exe11364_total_weight = 0.0
        exe22315_total_weight = 0.0
        category_max_weight = 0
        regular_total_weight = 0
        lq_total_weight = 0.0
        counter_22315 = 0
        counter_lq = 0
        exention_type = None

        categories_ids = []
        elements = []

        docids = docids
        model = 'stock.batch.delivery'
        batch_delivery_id = self.env[model].browse(docids)
        batch_delivery_id.ensure_one()

        moves = batch_delivery_id.move_lines.filtered(lambda x: x.quantity_done != 0.00 and x.product_tmpl_id.adr_idnumonu != False)
        sale_picks = batch_delivery_id.picking_ids
        partner_ids = batch_delivery_id.partner_ids

        for partner_id in partner_ids:
            partners_data.append(self.get_partner_data(partner_id))

        pickings = sale_picks
        company_id = pickings and pickings[0].company_id
        for pick in pickings:

            for line in pick.move_line_ids:
                product_tmpl_line = line.product_id.product_tmpl_id
                move_line = line.move_id

                if product_tmpl_line.adr_idnumonu:
                    ## Metemos el id en partners para tener un listado de los destinatarios.
                    partner_pickings.append({
                        'partner_id': line.move_id.partner_id.id,
                        'line_id': line.id,
                        'origin': move_line.origin,
                        'name': product_tmpl_line.name,
                        'default_code': product_tmpl_line.default_code,
                        'adr_denomtecnica': product_tmpl_line.adr_idnumonu.denomtecnica,
                        'adr_qty_limit': product_tmpl_line.adr_idnumonu.qty_limit,
                        'product_qty': line.qty_done,
                        'adr_bultodesc': product_tmpl_line.adr_idnumonu.bultodesc,
                        'packing_group': product_tmpl_line.adr_idnumonu.packing_group,
                        'official_name': product_tmpl_line.adr_idnumonu.official_name,
                        'ranking_id': product_tmpl_line.adr_idnumonu.ranking,
                        't_code': product_tmpl_line.adr_idnumonu.t_code,
                        'adr_exe22315': product_tmpl_line.adr_idnumonu.exe22315,
                        'adr_peligroma': product_tmpl_line.adr_idnumonu.peligroma,
                        'adr_weight_x_kgrs_11363': product_tmpl_line.adr_weight_x_kgrs_11363*line.qty_done,
                        'adr_weight_x_kgrs_11364': product_tmpl_line.adr_weight_x_kgrs_11364*line.qty_done,
                        'adr_acc_signals': product_tmpl_line.adr_idnumonu.acc_signals,
                        'adr_idnumonu': product_tmpl_line.adr_idnumonu.numero_onu,
                        'adr_regular_weight': product_tmpl_line.weight*line.qty_done,
                        'picking_id': line.picking_id.name,
                        'result_package_id': line.result_package_id and line.result_package_id.name,
                    })

                    if not product_tmpl_line.adr_idnumonu.exe22315 and not product_tmpl_line.adr_idnumonu.qty_limit > 0:
                        exe11363_total_weight = exe11363_total_weight + product_tmpl_line.adr_weight_x_kgrs_11363*line.qty_done
                        exe11364_total_weight = exe11364_total_weight + product_tmpl_line.adr_weight_x_kgrs_11364*line.qty_done
                        ## Guardamos las categorías diferentes
                        if not product_tmpl_line.adr_idnumonu.adr_category_id.id in categories_ids:
                            categories_ids.append(product_tmpl_line.adr_idnumonu.adr_category_id.id)
                    else:
                        if product_tmpl_line.adr_idnumonu.exe22315 and not product_tmpl_line.adr_idnumonu.qty_limit > 0:
                            exe22315_total_weight = exe22315_total_weight + product_tmpl_line.weight*line.qty_done
                            counter_22315 = counter_22315 + 1
                        else:
                            lq_total_weight = lq_total_weight + product_tmpl_line.weight*line.qty_done
                            counter_lq = counter_lq + 1

        if len(categories_ids) > 1:
            exention_type = '1.1.3.6.3'
            # Saco el máximo igualmente por no ponerlo directamente igual a 1000. Así al menos es modificable.
            category_obj = self.env['adr.code.category'].browse(categories_ids[0])
            category_max_weight = category_obj.max_weight_11363
            regular_total_weight = exe11363_total_weight
        else:
            if len(categories_ids) == 1:
                exention_type = '1.1.3.6.4'
                category_obj = self.env['adr.code.category'].browse(categories_ids[0])
                category_max_weight = category_obj.max_weight_11364
                regular_total_weight = exe11364_total_weight
        
        company_data = {
            'logo_web': company_id.logo_web,
            'vat': company_id.vat
        }

        delivery_carrier_data = {
            'vat': batch_delivery_id.driver_id.vat,
            'vehicle': batch_delivery_id.plate_id.name
        }
        
        #Ordeno el listado por orden de venta.

        partner_pickings.sort(key=lambda x: x['origin'], reverse=False)

        elements.append({
            'partners': partners_data,
            'movements': partner_pickings,
            'categories_ids': categories_ids
        })

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'docs': batch_delivery_id,
            'elements': elements,
            'exention_type': exention_type,
            'category_max_weight': category_max_weight,
            'regular_total_weight': "%.2f" % round(regular_total_weight,2),
            'exe22315_total_weight': "%.2f" % round(exe22315_total_weight,2),
            'counter_22315': counter_22315,
            'lq_total_weight': "%.2f" % round(lq_total_weight,2),
            'counter_lq': counter_lq,
            'company_data': company_data,
            'company_id': company_id,
            'delivery_carrier_data': delivery_carrier_data
        }
        return docargs

    def get_partner_data(self, partner_id):
        return {
            'id': partner_id.id,
            'name': partner_id.name,
            'street': partner_id.street,
            'street2': partner_id.street2,
            'zip': partner_id.zip,
            'city': partner_id.city,
            'state_id': partner_id.state_id.name,
            'country_id': partner_id.country_id.name
        }