# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import logging

_logger = logging.getLogger(__name__)

class StockWarehouseSGA(models.Model):

    _inherit = "stock.warehouse"
    sga_integrated = fields.Boolean('Integrado con Adaia',
                                    help="If checked, odoo will export this pick type to Adaia")

    def import_adaia(self, file_id, code):
        res = False
        sga_file_obj = self.env['sga.file'].browse(file_id)
        sga_file = open(sga_file_obj.sga_file, 'r')
        sga_file_lines = sga_file.readlines()
        sga_file.close()
        str_error = ''
        bool_error = True
        n_line = 0
        actual_product = False
        _logger.info("Importando fichero con código: {}".format(code))
        location_dest_id = self.env['stock.location'].search([('sga_integration_type', '=', 'sga_adaia')])
        for line in sga_file_lines:
            if code == 'TRS':
                if '|' in line:
                    file_data = line.rsplit('|')
                    TIPEREG = file_data[0]
                    ARTREF = file_data[2]
                n_line += 1
                
                if TIPEREG == 'STAJ':
                    actual_product = self.env['product.product'].search([('default_code', '=', ARTREF)])
                    product = actual_product.with_context(location=location_dest_id.id)

                    _logger.info("Procesando el producto: {}".format(product.display_name))

                    if not product:
                        bool_error = False
                        str_error += "Codigo de producto %s no encontrado...%s " % (ARTREF, n_line)
                        error_message =  u'Producto %s no encontrado.' % (
                                        ARTREF)
                        _logger.info("Error: {}".format(error_message))
                        self.create_sga_file_error(sga_file_obj, n_line, 'TRS', product.display_name, 'Producto no válido', error_message)

                        sga_file_obj.write_log(str_error)
                        continue
                    else:
                        SIGNO = file_data[3]
                        th_qty = product.qty_available
                        inventory = self.env['stock.inventory']
                        CAN = file_data[4]

                        if SIGNO == '+':
                            _logger.info("Añadiendo {} unidad(es) al producto: {}".format(CAN, product.display_name))
                            
                            line = {
                                'product_qty': CAN,
                                'location_id': location_dest_id.id,
                                'product_id': product.id,
                                'product_uom_id': product.uom_id.id,
                                'theoretical_qty': th_qty
                            }

                        elif SIGNO == '-':
                            _logger.info("Restando {} unidad(es) al producto: {}".format(CAN, product.display_name))

                            line = {
                                'product_qty': CAN,
                                'location_dest_id': location_dest_id.id,
                                'product_id': product.id,
                                'product_uom_id': product.uom_id.id,
                                'theoretical_qty': th_qty
                            }
                        else:
                            _logger.info("Signo {} no reconocible.".format(SIGNO))
                            bool_error = False
                            str_error += "Signo %s no reconocible...%s " % (ARTREF, n_line)
                            error_message =  u'Signo %s no reonocile.' % (
                                            SIGNO)
                            _logger.info("Error: {}".format(error_message))
                            self.create_sga_file_error(sga_file_obj, n_line, 'TRS', product.display_name, 'Signo no válido', error_message)

                            sga_file_obj.write_log(str_error)
                            continue

                        inventory = Inventory.create({
                            'name': _('INV: {}').format(product.display_name),
                            'filter': 'product',
                            'product_id': product.id,
                            'location_id': location_dest_id.id,
                            'line_ids': [(0, 0, line)],
                        })
                        inventory.action_done()
        return res

    def create_sga_file_error(self, sga_file_obj, n_line, sga_operation, pick, error_code, error_message):
        error_vals = {'file_name': sga_file_obj.name,
                      'sga_file_id': sga_file_obj.id,
                      'line_number': n_line,
                      'sga_operation': sga_operation,
                      'object_type': sga_operation,
                      'object_id': pick.name,
                      'date_error': sga_file_obj.name[5:19].strip(),
                      'error_code': error_code,
                      'error_message': error_message}
        self.env['sga.file.error'].create(error_vals)