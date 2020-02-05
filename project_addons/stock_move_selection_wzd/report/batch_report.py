# Copyright 2018 Comunitea - Kiko Sánchez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class ReportPrintBatchPicking(models.AbstractModel):
    _inherit = 'report.stock_batch_picking.report_batch_picking'

    @api.model
    def key_level_0(self, operation, code=''):

        if code == 'outgoing':
            res = operation.move_id.sale_line_id.order_id
        elif code == 'incoming':
            res = operation.move_id.purchase_line_id.order_id
        elif code == 'picking':
            res = operation.move_id.picking_type_id.name
        elif code == 'location':
            res = operation.location_dest_id.id, operation.location_id.id
        else:

            res = operation.location_id.id, operation.location_dest_id.id
        return res

    @api.model
    def key_level_1(self, operation, code=''):

        if code == 'outgoing':
            prev_picking = operation.move_id.move_orig_ids.mapped("picking_id")
            res = prev_picking
        elif code == 'picking':
            res = operation.location_id.id, operation.location_dest_id.id
        else:
            res = operation.move_id.partner_id
        return res

    @api.model
    def key_level_2(self, operation, code=''):
        return operation.product_id

    @api.model
    def new_level_0(self, operation, code=''):

        if code == 'outgoing':
            picking_id = operation.move_id.move_orig_ids.mapped("picking_id")
            sale_id = operation.move_id.sale_line_id.order_id
            level_0_name = u'Pedido: {} S/Ref {} : {}'.format(
            sale_id.name, sale_id.client_order_ref or sale_id.origin, sale_id.date_order.split()[0])
            res = {
                'name': sale_id.name,
                'display_name': level_0_name,
                'date': sale_id.confirmation_date,
                'location': operation.location_id,
                'location_dest': operation.location_dest_id,
                'l1_items': {},
            }
        elif code == 'picking':
            picking_id = operation.move_id.picking_id
            sale_id = operation.move_id.sale_line_id.order_id
            res = {
                'name': operation.move_id.picking_type_id.name,
                'display_name': sale_id.name ,
                'date': operation.move_id.picking_id.date,
                'location': operation.location_id,
                'location_dest': operation.location_dest_id,
                'l1_items': {},
            }

        else:
            ##todo pasarlo a warehouse_pasillo???p.e.
            picking_id = operation.move_id.picking_id
            level_0_name = u'{} \u21E8 {}'.format(
            operation.location_id.name_get()[0][1],
            operation.location_dest_id.name_get()[0][1])
            res = {
                'name': level_0_name,
                'display_name': level_0_name,
                'date': picking_id.scheduled_date,
                'location': operation.location_id,
                'location_dest': operation.location_dest_id,
                'l1_items': {},
            }
        return res

    @api.model
    def new_level_1(self, operation, code=''):
        picking_id = operation.move_id.move_orig_ids.mapped("picking_id")
        if code == 'outgoing':
            level_1_name = u'-------------------------- Origen \u21E8 {}'.format(picking_id.mapped('name')[0])
            return {
                'name': picking_id.name,
                'display_name': level_1_name,
                'date': picking_id.scheduled_date,
                'location': operation.location_id,
                'location_dest': operation.location_dest_id,
                'l2_items': {},
            }
        else:
            level_1_name = u'{} \u21E8 {}'.format(
                operation.location_id.name,
                operation.location_dest_id.name)
            res = {
                'name': operation.display_name,
                'date': picking_id.scheduled_date,
                'display_name': level_1_name,
                'location': operation.location_id,
                'location_dest': operation.location_dest_id,
                'l2_items': {},
            }
        return res

    @api.model
    def new_level_2(self, operation, code =''):
        sale_line_id = operation.move_id.sale_line_id
        if operation.state == 'done':
            qty = operation.qty_done
        else:
            qty = operation.product_qty
        res = {
            'product': operation.product_id,
            'product_qty': qty,
            'operations': operation,
            'location_id': operation.location_id.name,
            'location_dest_id': operation.location_dest_id.name,
            'package_id': operation.package_id.name,
            'result_package_id': operation.result_package_id.name,
            'flecha': u'\u21E8'

        }
        if sale_line_id:
            ##replico el create invoice de create invoice

            res.update({
                'price_unit': sale_line_id and sale_line_id.price_unit or 0.00,
                'dto': sale_line_id and sale_line_id.chained_discount or 0,
                'subtotal': sale_line_id and sale_line_id.price_subtotal or 0.00,
                'tax': sale_line_id and sale_line_id.mapped('tax_id') or 0,
                })
        else:
            res.update({
                'price_unit': operation.product_id.lst_price,
                'dto': 0,
                'subtotal': operation.product_id.lst_price * qty,
                'tax': operation.move_id._compute_tax_id()
            })
        return res

    @api.model
    def get_package_line(self, line):

        tax = line._compute_tax_id()
        qty = sum(x.qty_done for x in line.move_line_ids)
        res = {
            'product_id': line.product_id,
            'product': line.product_id.name,
            'product_qty': qty,
            'price_unit': line.product_id.lst_price,
            'dto': 0,
            'subtotal': line.product_id.lst_price * qty,
            'tax': ', '.join(map(lambda x: x.amount.is_integer() and str(int(x.amount)) + '%' or str(x.amount) + '%', line._compute_tax_id())),
            'flecha': u'\u21E8'
        }
        return res

    @api.model
    def update_level_2(self, group_dict, operation, code=''):
        group_dict['product_qty'] += (
                operation.product_qty or operation.qty_done)
        group_dict['operations'] += operation

    @api.model
    def sort_level_0(self, rec_list, code=''):
        print (rec_list)
        if code == 'outgoing':
            return sorted(rec_list, key=lambda rec: (rec['date']))
        else:
            return sorted(rec_list, key=lambda rec: (
                rec['location'].posx, rec['location'].posy, rec['location'].posz,
                rec['location'].name))

    @api.model
    def sort_level_1(self, rec_list, code=''):
        print(rec_list)
        if code == 'outgoing':
            return sorted(rec_list, key=lambda rec: (rec['name']))
        else:
            return sorted(rec_list, key=lambda rec: (
                rec['location'].posx, rec['location'].posy, rec['location'].posz,
                rec['location'].name))

    @api.model
    def sort_level_2(self, rec_list, code):
        return sorted(rec_list, key=lambda rec: (
            rec['product'].default_code or '', rec['product'].id))


    @api.model
    def _get_grouped_data(self, batch):
        print ('Datos del Batch {} / {}'.format(batch.name, batch.picking_type_id.group_code.code))
        grouped_data = {}
        code = batch.picking_type_id.group_code.code
        op_ids = batch.move_line_ids
        move_ids = op_ids.mapped('move_id')

        #prev_picks = move_ids.mapped('move_orig_ids').mapped("picking_id")
        #sales = move_ids.mapped('sale_line_id').mapped('order_id')


        for op in op_ids:
            move_id = op.move_id
            #prev_pick_ids = move_id.mapped('move_orig_ids').mapped("picking_id")
            #sale_ids = move_id.mapped('sale_line_id').mapped('order_id')

            l0_key = self.key_level_0(op, code)
            if l0_key not in grouped_data:
                grouped_data[l0_key] = self.new_level_0(op, code)

            l1_key = self.key_level_1(op, code)
            if l1_key not in grouped_data[l0_key]['l1_items']:
                grouped_data[l0_key]['l1_items'][l1_key] = self.new_level_1(op, code)

            l2_key = self.key_level_2(op, code)

            if l2_key in grouped_data[l0_key]['l1_items'][l1_key]['l2_items']:
                self.update_level_2(grouped_data[l0_key]['l1_items'][l1_key]['l2_items'][l2_key], op, code)
            else:
                grouped_data[l0_key]['l1_items'][l1_key]['l2_items'][l2_key] = self.new_level_2(op, code)


        for l0_key in grouped_data.keys():
            for l1_key in grouped_data[l0_key]['l1_items']:
                grouped_data[l0_key]['l1_items'][l1_key]['l2_items'] = self.sort_level_2(grouped_data[l0_key]['l1_items'][l1_key]['l2_items'].values(), code)
            grouped_data[l0_key]['l1_items'] = self.sort_level_1(grouped_data[l0_key]['l1_items'].values(), code)


        res = self.sort_level_0(grouped_data.values(), code)
        return res

    @api.model
    def _get_grouped_packs(self, batch):
        pack_line = {}
        for line in batch.pack_lines_picking_id.move_lines:
            product = line.product_id
            if product in pack_line:
               pack_line[product].qty += line.qty_done
            else:
                pack_line[product] = self.get_package_line(line)
        return pack_line.values()

    @api.model
    def get_report_values(self, docids, data=None):
        model = 'stock.batch.picking'
        docs = self.env[model].browse(docids)
        grouped_data = self._get_grouped_data(docs)
        res = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'grouped_data': grouped_data,
            'now': fields.Datetime.now,
        }
        if docs.pack_lines_picking_id:
            res.update({'doc_package': self._get_grouped_data(docs.pack_lines_picking_id)})

        return res