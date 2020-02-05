# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DeliveryBatchReport(models.AbstractModel):
    _name = 'report.stock_move_selection_wzd.delivery_batch_view'

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model', 'stock.batch.delivery')
        delivery_id = self.env[model].browse(docids)
        domain = [('batch_delivery_id', '=', docids), ('state', '!=', 'cancel')]
        move_ids = self.env['stock.move'].search(domain)
        picking_ids = move_ids.mapped('picking_id')
        partner_ids = move_ids.mapped('partner_id')

        info_partner_ids = []
        ctx = self._context.copy()

        seq_partner_ids = self.env['delivery.partner.order'].search([('delivery_id', '=', delivery_id.id)])
        if not seq_partner_ids:
            seq_partner_ids = delivery_id.create_partner_order()


        for order_line in seq_partner_ids:

            partner_id = order_line.partner_id
            delivery_route_id = delivery_id.delivery_route_path_id
            partner_order = order_line.sequence
            ctx.update(partner_id=partner_id.id)
            info_partner = delivery_id.get_delivery_info (partner_id=partner_id)
            str_pick = ''
            for picking_id in info_partner['batch_ids']:
                if str_pick:
                    str_pick = '{},{}'.format(str_pick, picking_id['name'])
                else:
                    str_pick = picking_id['name']

            manual_moves = move_ids.filtered(lambda x: x.partner_id == partner_id and x.product_id.manual_picking)
            info_partner.update({
                'route': delivery_route_id,
                'partner_id': partner_id,
                'str_pick': str_pick,
                'count_pick': len(info_partner['batch_ids']),
                'manual_moves': manual_moves,
                'partner_order': partner_order
            })
            info_partner_ids.append(info_partner)

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'docs': delivery_id,
            'partner_data': info_partner_ids,
            'manual_moves': manual_moves,

        }
        print (docargs)
        return docargs

    def get_report_values2(self, docids, data=None):
        model = self.env.context.get('active_model', 'stock.batch.delivery')
        batch = self.env[model].browse(docids)
        domain = [('batch_delivery_id', '=', docids), ('state', '!=', 'cancel')]
        move_ids = self.env['stock.move'].search(domain)
        pickings = move_ids.mapped('batch_picking_id')
        company_id = batch.picker_id and batch.picker_id.company_id or self.env.user.company_id
        company_data = {
            'logo_web': company_id.logo_web,
            'vat': company_id.vat
        }
        move_line_ids = move_ids.mapped('move_line_ids')
        picking_ids = move_ids.mapped('picking_id')
        package_ids = move_line_ids.mapped('result_package_id')


        delivery_carrier_data = {
            'vat': batch.driver_id.vat,
            'vehicle': batch.plate_id
        }

        elements = []
        partners_data = []
        partners_index = []
        partner_pickings = []
        partner_ids = []
        for pick in pickings:
            for line in pick.move_line_ids:
                product_tmpl_line = line.product_id.product_tmpl_id
                move_line = line.move_id
                ## Metemos el id en partners para tener un listado de los destinatarios.
                if not line.partner_id in partner_ids:
                    partner_ids.append(line.partner_id)
                if not move_line.partner_id.id in partners_index:
                    partners_index.append(move_line.partner_id.id)
                    partners_data.append({
                        'id': move_line.partner_id.id,
                        'name': move_line.partner_id.name,
                        'street': move_line.partner_id.street,
                        'street2': move_line.partner_id.street2,
                        'zip': move_line.partner_id.zip,
                        'city': move_line.partner_id.city,
                        'state_id': move_line.partner_id.state_id.name,
                        'country_id': move_line.partner_id.country_id.name
                    })
                partner_pickings.append({
                    'partner_id': move_line.partner_id.id,
                    'partner_name': move_line.partner_id.display_name,
                    'line_id': line.id,
                    'origin': move_line.origin,
                    'name': product_tmpl_line.name,
                    'default_code': product_tmpl_line.default_code,
                    'product_qty': line.qty_done,
                    'picking_id': line.batch_picking_id.name,
                    'result_package_id': line.result_package_id.name
                })

        elements.append({
            'partners': partners_data,
            'movements': partner_pickings
        })

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'partner_ids': partner_ids,
            'docs': batch,
            'elements': elements,
            'company_data': company_data,
            'company_id': company_id,
            'delivery_carrier_data': delivery_carrier_data,
            'pickings': pickings
        }
        print (docargs)
        return docargs