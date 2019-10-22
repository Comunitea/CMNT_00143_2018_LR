# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError
from .res_config import SGA_STATES


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    sga_state = fields.Selection(SGA_STATES)
    ulma_error = fields.Text(default="", string="Error msg in case the Ulma integration failed")

    @api.multi
    def send_to_ulma(self):
        for package in self:
            cont = 1
            flag = True
            try:
                for move_line in package.move_line_ids:
                    des = move_line.product_id.product_tmpl_id.name
                    line_values_to_send = {
                        'mmmabclog': move_line.product_id.abc_classification[0],
                        'mmmacccolcod': package.id,
                        'mmmartdes': (des[:40]) if len(des) > 40 else des,
                        'mmmartref': move_line.product_id.product_tmpl_id.default_code,
                        'mmmcanuni': move_line.qty_done,
                        'mmmcntdorref': package.name,
                        'mmmcmdref': 'ENT',
                        'mmmcrirot': cont,
                        'mmmdim': "CP"+str(len(move_line)),
                        'mmmdisref': "SUBPAL",
                        'mmmges': "ULMA",
                        'mmmlot': None,
                        'mmmres': None,
                        'mmmsecada': move_line.id,
                        'mmmsesid': 1,
                        'mmmubidesref': "01P010011",
                        'mmmzondesref': move_line.product_id.abc_classification[0],
                        'momcre': datetime.datetime.now(),
                        'mmmartean': None,
                        'mmmacccod': move_line.id,
                        'mmmdorhue': cont,
                        'mmmfeccad': None,
                        'mmmmomexp': None,
                        'mmmmonlot': 1,
                        'mmmrecref': 0,
                        'mmmartapi': 0
                    }
                    cont += 1
                    flag = self.env['ulma.mmmout'].create(line_values_to_send)
                
                line_values_to_send = {
                    'mmmacccolcod': package.id,
                    'mmmcmdref': 'ENT',
                    'mmmcntdorref': package.name,
                    'mmmdisref': "SUBPAL",
                    'mmmges': "ULMA",
                    'mmmres': "FIN",
                    'mmmsecada': move_line.id,
                    'mmmsesid': 1,
                    'mmmubidesref': "01P010011",
                    'mmmdim': "CP"+str(len(move_line)),
                    'momcre': datetime.datetime.strptime(move_line.create_date, '%Y-%m-%d %H:%M:%S.%f'),
                    'mmmartean': None,
                    'mmmacccod': 0,
                    'mmmfeccad': '01/01/2050',
                    'mmmmomexp': None,
                    'mmmmonlot': None,
                    'mmmrecref': 0
                }
                flag = self.env['ulma.mmmout'].create(line_values_to_send)
                
                if flag == True:
                    package.write({
                        'sga_state': 'pending'
                    })                
                    
            except Exception as error:                  
                raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)
                
    @api.multi
    def get_from_ulma(self):
        flag_type = 0
        try:
            for package in self:
                data = self.env['ulma.mmminp'].search([('mmmacccolcod', '=', package.id), ('mmmres', '=', 'FIN')])
                ulma_obj = self.env['ulma.mmminp'].browse(data.id)
                if not ulma_obj:
                    flag_type = 2
                elif ulma_obj.mmmcmdref == 'ERR':
                    package.write({
                        'sga_state': 'import_error',
                        'ulma_error': ulma_obj.mmmresmsj
                    })
                    flag_type = 1
                elif ulma_obj.mmmcmdref == 'ENT':
                    package.write({
                        'sga_state': 'pending'
                    })
                return flag_type
        except Exception as error:                  
            raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)
                   