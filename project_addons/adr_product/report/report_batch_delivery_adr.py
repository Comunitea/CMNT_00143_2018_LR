# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BatchDeliveryCustomReport(models.AbstractModel):
    _name = 'report.adr_product.batch_delivery_adr_view'

    def get_report_values(self, docids, data=None):

        partners_data = []
        partner_pickings = []
        exe11363_total_weight = 0.0
        exe11364_total_weight = 0.0
        real_total_weight_1136x = 0.0
        category_max_weight = 0
        regular_total_weight = 0
        real_total_weight = 0
        exention_type = None

        docids = docids
        model = 'stock.batch.delivery'
        batch_delivery_id = self.env[model].browse(docids)
        batch_delivery_id.ensure_one()

        moves = batch_delivery_id.move_lines.filtered(lambda x: x.quantity_done != 0.00 and x.product_tmpl_id.adr_idnumonu)
        if not moves:
            raise ValidationError(_("There are no ADR products in this order."))

        move_line_ids = self.env['stock.move.line'].search([('move_id', 'in', moves.ids)])
        pickings = moves.mapped('picking_id')
        product_ids = moves.mapped('product_id')
        partner_ids = pickings.mapped('partner_id')
        packages = move_line_ids.mapped('result_package_id')

        # 1136x
        exec1136x_data = self.get_exec_type_data('1136x', move_line_ids)
        real_total_weight = exec1136x_data['cats_weight']['real'] if exec1136x_data['cats_weight']['real'] else 0.0

        # 22315
        exec22315_data = self.get_exec_type_data('22315', move_line_ids)

        # LQ
        execlq_data = self.get_exec_type_data('lq', move_line_ids)

        if len(exec1136x_data['categories']) > 1:
            exention_type = '1.1.3.6.3'
            regular_total_weight = exec1136x_data['cats_weight']['weight_11363'] if exec1136x_data['cats_weight']['weight_11363'] else 0.0
        else:
            if len(exec1136x_data['categories']) == 1:
                exention_type = '1.1.3.6.4'
                regular_total_weight = exec1136x_data['cats_weight']['weight_11364'] if exec1136x_data['cats_weight']['weight_11364'] else 0.0

        packages_count = len(packages)

        for partner_id in partner_ids:
            partners_data.append(self.get_partner_data(partner_id, move_line_ids))
        
        partners_data.sort(key=lambda x: x['adr_sequence'], reverse=False)

        company_id = pickings and pickings[0].company_id
        for pick in pickings:

            pick_header = "{}".format(pick.name)
            pick_lines = []
            tracking = []
            real_kgs_picking = 0.0
            kgs_picking_11363 = 0.0
            kgs_picking_11364 = 0.0
            for line in move_line_ids.filtered(lambda x: x.picking_id == pick):
                pick_lines.append({
                    'result_package_id' : line.result_package_id and line.result_package_id.name,
                    'product_qty': line.qty_done,
                    'name': line.product_id.product_tmpl_id.name,
                    'default_code': line.product_id.product_tmpl_id.default_code
                })
            
            partner_pickings.append({
                'header': pick_header,
                'lines': pick_lines
            })
        
        company_data = {
            'logo_web': company_id.logo_web,
            'vat': company_id.vat
        }

        delivery_carrier_data = {
            'vat': batch_delivery_id.driver_id.vat,
            'vehicle': batch_delivery_id.plate_id.name
        }

        docargs = {
            'exec1136x_data': exec1136x_data,
            'exec22315_data': exec22315_data,
            'execlq_data': execlq_data,
            'doc_ids': docids,
            'doc_model': model,
            'docs': batch_delivery_id,
            'exention_type': exention_type,
            'category_max_weight': category_max_weight,
            'regular_total_weight': "%.2f" % round(regular_total_weight,2),
            'real_total_weight': "%.2f" % round(real_total_weight,2),
            'company_data': company_data,
            'company_id': company_id,
            'delivery_carrier_data': delivery_carrier_data,
            'packages_count': packages_count,
            'partners': partners_data,
            'partner_pickings': partner_pickings
        }
        return docargs

    def get_partner_data(self, partner_id, move_line_ids):

        partner_string = "{} {} {} - {} - {} - {}".format(partner_id.name, partner_id.street if partner_id.street else '', \
            partner_id.street2 if partner_id.street2 else '', partner_id.zip if partner_id.zip else '', \
            partner_id.state_id.name if partner_id.state_id else '', partner_id.country_id.name if partner_id.country_id else '')
        
        pickings = []

        move_lines = self.env['stock.move.line'].search([('id', 'in', move_line_ids.ids), ('partner_id', '=', partner_id.id)])

        real_kgs_picking = 0.0
        kgs_picking_11363 = 0.0
        kgs_picking_11364 = 0.0

        for move in move_lines:
            move_string = "{} [{}/{}]".format(move.picking_id.name, "LQ" if \
                not move.product_id.product_tmpl_id.adr_exe22315 and \
                move.product_id.product_tmpl_id.adr_idnumonu.qty_limit >= move.product_id.product_tmpl_id.weight else \
                move.product_id.product_tmpl_id.adr_idnumonu.acc_signals or '', \
                move.product_id.product_tmpl_id.adr_idnumonu.numero_onu or '')
            pickings.append(move_string)
        
            if not move.product_id.product_tmpl_id.adr_exe22315 and not move.product_id.product_tmpl_id.adr_idnumonu.qty_limit>= move.product_id.product_tmpl_id.weight:
                real_kgs_picking = real_kgs_picking + move.qty_done*move.product_id.product_tmpl_id.weight
                kgs_picking_11363 = kgs_picking_11363 + move.product_id.product_tmpl_id.adr_weight_x_kgrs_11363*move.qty_done
                kgs_picking_11364 = kgs_picking_11364 + move.product_id.product_tmpl_id.adr_weight_x_kgrs_11364*move.qty_done

        return {
            'partner_string': partner_string,
            'pickings': pickings,
            'name': partner_id.name,
            'packs': len(move_lines.filtered(lambda x: not x.product_id.product_tmpl_id.adr_exe22315 and\
                    not x.product_id.product_tmpl_id.adr_idnumonu.qty_limit >= x.product_id.product_tmpl_id.weight).mapped('result_package_id')) or 0.0,
            'real_kgs_picking': real_kgs_picking,
            'kgs_picking_11363': kgs_picking_11363,
            'kgs_picking_11364': kgs_picking_11364,
            'adr_sequence': partner_id.adr_sequence
        }

    def get_exec_type_weight_strings(self, exec_type, move_line_ids, products):
        real_weight = 0.0
        weight_11363 = 0.0
        weight_11364 = 0.0

        cat_weight = [0.0,0.0,0.0,0.0,0.0]

        for cat_id in [1,2,3,4]:
            cat_weight_11363 = 0.0
            cat_weight_11364 = 0.0
            cat_weight[cat_id] = 0.0
            
            for move_line in move_line_ids.filtered(lambda x: x.product_id.product_tmpl_id.adr_idnumonu.\
                adr_category_id.id == cat_id):
                real_weight = real_weight + move_line.product_id.product_tmpl_id.weight*move_line.qty_done

                if exec_type == '1136x':
                    weight_11363 = weight_11363 + \
                        move_line.product_id.product_tmpl_id.adr_weight_x_kgrs_11363*move_line.qty_done
                    weight_11364 = weight_11364 + \
                        move_line.product_id.product_tmpl_id.adr_weight_x_kgrs_11364*move_line.qty_done
                    cat_weight_11363 = cat_weight_11363 + move_line.product_id.product_tmpl_id.adr_weight_x_kgrs_11363*move_line.qty_done
                    cat_weight_11364 = cat_weight_11364 + move_line.product_id.product_tmpl_id.adr_weight_x_kgrs_11364*move_line.qty_done
                else:
                    cat_weight[cat_id] = cat_weight[cat_id] + move_line.product_id.product_tmpl_id.weight*move_line.qty_done

            if exec_type == '1136x':
                cat_weight[cat_id] = {
                    '11363': cat_weight_11363,
                    '11364': cat_weight_11364
                }
        
        if exec_type == '1136x':
            string_11363 = "Peso total: {}<1000. Transporte acogido a la exención 1.1.3.6.3 ADR".format(weight_11363)
            string_11364 = "Peso total: {}<1000. Transporte acogido a la exención 1.1.3.6.4 ADR".format(weight_11364)
            string_cats_11363 = "Peso cat. 1: {} Peso cat. 2: {} Peso cat. 3: {} Peso cat. 4: {}".format(cat_weight[1]['11363'] \
                if cat_weight[1] != 0.0 else 0.0, cat_weight[2]['11363'] if cat_weight[2] != 0.0 else 0.0, \
                cat_weight[3]['11363']  if cat_weight[3] != 0.0 else 0.0, cat_weight[4]['11363'] if cat_weight[4] != 0.0 else 0.0)
            string_cats_11364 = "Peso cat. 1: {} Peso cat. 2: {} Peso cat. 3: {} Peso cat. 4: {}".format(cat_weight[1]['11364'] \
                if cat_weight[1] != 0.0 else 0.0, cat_weight[2]['11364'] if cat_weight[2] != 0.0 else 0.0, \
                cat_weight[3]['11364'] if cat_weight[3] != 0.0 else 0.0, cat_weight[4]['11364'] if cat_weight[4] != 0.0 else 0.0)

            return {
                'real': real_weight,
                'weight_11363': weight_11363,
                'weight_11364': weight_11364,
                'string_11363': string_11363,
                'string_11364': string_11364,
                'string_cats_11363': string_cats_11363,
                'string_cats_11364': string_cats_11364,
                'product_data_11363': self.get_product_data('11363', products, move_line_ids),
                'product_data_11364': self.get_product_data('11364', products, move_line_ids)
            }
        else:
            if exec_type == '22315':
                string = "Peso total: {}. Transporte acogido a la exención 2.2.3.1.5 ADR".format(real_weight)
            else:
                string = "Peso total: {}. Transporte acogido a la exención por cantidades limitadas".format(real_weight)
            string_cats = "Peso cat. 1: {}  Peso cat. 2: {}  Peso cat. 3: {}  Peso cat. 4: {}".format(cat_weight[1], \
                cat_weight[2], cat_weight[3], cat_weight[4])

            return {
                'string': string,
                'string_cats': string_cats,
                'product_data': self.get_product_data(exec_type, products, move_line_ids)
            }

    def get_exec_type_data(self, exec_type, move_line_ids):
        if exec_type == '1136x':
            move_line_ids = move_line_ids.filtered(lambda x: not x.product_id.product_tmpl_id.adr_exe22315 and\
                not x.product_id.product_tmpl_id.adr_idnumonu.qty_limit >= x.product_id.product_tmpl_id.weight)
        elif exec_type == '22315':
            move_line_ids = move_line_ids.filtered(lambda x: x.product_id.product_tmpl_id.adr_exe22315)
        elif exec_type == 'lq':
            move_line_ids = move_line_ids.filtered(lambda x: not x.product_id.product_tmpl_id.adr_exe22315 and\
                x.product_id.product_tmpl_id.adr_idnumonu.qty_limit >= x.product_id.product_tmpl_id.weight)

        products = move_line_ids.mapped('product_id')
        categories = products.mapped('product_tmpl_id').mapped('adr_idnumonu').mapped('adr_category_id')
        cats_weight = self.get_exec_type_weight_strings(exec_type, move_line_ids, products)

        return {
            'move_lines': move_line_ids,
            'products': products,
            'categories': categories,
            'cats_weight': cats_weight
        }

    def get_product_data(self, exec_type, products, move_line_ids):
        product_data = []
        for product in products:
            moves = move_line_ids.filtered(lambda x: x.product_id == product)
            qty_done = 0.0
            for move in moves:
                qty_done += move.qty_done
            
            packages = len(moves.mapped('result_package_id'))

            product_string = "UN {} {}".format(product.product_tmpl_id.adr_idnumonu.numero_onu or '', \
                product.product_tmpl_id.adr_idnumonu.official_name or '')
            
            if product.product_tmpl_id.adr_denomtecnica:
                product_string += " ({})".format(product.product_tmpl_id.adr_denomtecnica)
            
            if product.product_tmpl_id.adr_idnumonu.acc_signals:
                product_string += ", {}".format(product.product_tmpl_id.adr_idnumonu.acc_signals)

            if product.product_tmpl_id.adr_idnumonu.packing_group:
                product_string += ", {}".format(product.product_tmpl_id.adr_idnumonu.packing_group)
            
            if product.product_tmpl_id.adr_idnumonu.ranking:
                product_string += ", {}".format(product.product_tmpl_id.adr_idnumonu.ranking)
            
            if product.product_tmpl_id.adr_idnumonu.t_code:
                product_string += ", ({})".format(product.product_tmpl_id.adr_idnumonu.t_code)

            if product.product_tmpl_id.adr_peligroma:
                product_string += ", peligroso para el medioambiente"
            
            if exec_type == '11363':   
                product_weight = "Peso: {} Kg.".format(qty_done*product.product_tmpl_id.adr_weight_x_kgrs_11363)
            elif exec_type == '11364':
                product_weight = "Peso: {} Kg.".format(qty_done*product.product_tmpl_id.adr_weight_x_kgrs_11364)
            else:
                product_weight = "Peso: {} Kg.".format(qty_done*product.product_tmpl_id.weight)
            product_qty = "Bultos: {} Uds: {}".format(packages, qty_done)
            product_box = "Descripción embalaje: {}".format(product.product_tmpl_id.adr_bultodesc or '')

            product_data.append({
                'product_string': product_string,
                'product_qty': product_qty,
                'product_weight': product_weight,
                'product_box': product_box,
            })
        
        return product_data