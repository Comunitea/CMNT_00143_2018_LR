# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError
from pprint import pprint


class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"
    ulma_state = fields.Selection([('W', 'En espera'), ('P', 'Procesado'), ('E', 'Error'), ('N', 'Not sent')], default='N')


    def send_to_ulma(self):
        try:
            for batch in self:
                for pick in batch.picking_ids:
                    pick.send_to_ulma()                

                batch_values_to_send = {
                    'mmmcmdref': "SAL",
                    'mmmcod': batch.name,
                    'mmmdisref': "SUBPAL",
                    'mmmges': "ULMA",
                    'mmmres': "FINPED",
                    'mmmsesid': 2,
                    'momcre': datetime.datetime.now().date().strftime('%Y-%m-%d'),
                    'mmmartean': "ean13",
                    'mmmbatch': batch.name,
                    'mmmmomexp': batch.date
                }
                self.env['ulma.mmmout'].write_line(batch_values_to_send, 2, batch.id)
        except Exception as error:                  
            raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)              

    def get_from_ulma(self):
        try:
            for batch in self:
                flag_type = None
                for pick in batch.picking_ids:
                    flag_type = pick.get_from_ulma()

                if flag_type == 0:
                    batch.write({
                        'ulma_state': 'P'
                    })
                elif flag_type == 1:
                    batch.write({
                        'ulma_state': 'E'
                    })
        except Exception as error:                  
            raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)

class StockPicking(models.Model):

    _inherit = "stock.picking"
    ulma_state = fields.Selection([('W', 'En espera'), ('P', 'Procesado'), ('E', 'Error'), ('N', 'Not sent')], default='N')    
    ulma_error = fields.Text(default="", string="Error msg in case the Ulma integration failed")

    @api.multi
    def send_to_ulma(self):
        try:
            for pick in self:
                cont = 0
                if pick.move_line_ids:
                    for move_line in pick.move_line_ids:
                        des = move_line.product_id.product_tmpl_id.name
                        line_values_to_send = {
                            'mmmacccolcod': pick.id,
                            'mmmartdes':  (des[:40]) if len(des) > 40 else des,
                            'mmmartref': move_line.product_id.product_tmpl_id.default_code,
                            'mmmcanuni': move_line.ordered_qty,
                            'mmmcmdref': "SAL",
                            'mmmcod': 1,
                            'mmmdisref': "SUBPAL",
                            'mmmexpordref': pick.name,
                            'mmmges': "ULMA",
                            'mmmres': "",
                            'mmmsecada': move_line.id,
                            'mmmsesid': 2,
                            'momcre': datetime.datetime.strptime(move_line.create_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
                            'mmmartean': "ean13",
                            'mmmterref': None,
                            'mmmacccod': cont,
                            'mmmbatch': pick.batch_picking_id.name,
                            'mmmmomexp': datetime.datetime.strptime(pick.scheduled_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
                            'mmmfeccad': datetime.datetime.strptime(pick.scheduled_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
                            'mmmartapi': 0,
                            'mmmminudsdis': 1
                        }
                        self.env['ulma.mmmout'].write_line(line_values_to_send, 0, move_line.id)
                        cont += 1

                    pick_values_to_send = {
                        'mmmacccolcod': pick.id,
                        'mmmcmdref': "SAL",
                        'mmmcod': 1,
                        'mmmdisref': "SUBPAL",
                        'mmmentdes': str(pick.partner_id.name)+'('+str(pick.name)+')',
                        'mmmexpordref': 'N('+str(pick.name)+')',
                        'mmmges': "ULMA",
                        'mmmres': "FIN",
                        'mmmsesid': 2,
                        'momcre': datetime.datetime.strptime(pick.create_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
                        'mmmartean': "ean13",
                        'mmmterref': pick.partner_id.ref,
                        'mmmentdir1': str(pick.partner_id.street)+str(pick.partner_id.street2),
                        'mmmentdir2': pick.partner_id.city,
                        'mmmentdir3': pick.partner_id.state_id.name,
                        'mmmentdir4': pick.partner_id.zip,
                        'mmmbatch': pick.batch_picking_id.name,
                        'mmmmomexp': datetime.datetime.strptime(pick.scheduled_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
                        'mmmurgnte': 'N',
                        'mmmtraref': str(pick.batch_picking_id.shipping_type)+'-N'
                    }
                    self.env['ulma.mmmout'].write_line(pick_values_to_send, 1, pick.id)
        except Exception as error:                  
            raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)
    
    @api.multi
    def get_from_ulma(self):
        flag_type = 0
        try:
            for pick in self:
                data = self.env['ulma.mmminp'].search([('mmmexpordref', '=', pick.name), ('mmmres', '=', 'FIN')])
                ulma_obj = self.env['ulma.mmminp'].browse(data.id)
                if not ulma_obj:
                    flag_type = 2
                elif ulma_obj.mmmcmdref == 'ERR':
                    pick.write({
                        'ulma_error': ulma_obj.mmmresmsj or ulma_obj.mmmerrmsj
                    })
                    flag_type = 1
                elif ulma_obj.mmmcmdref == 'SAL':
                    moves_ids = self.env['ulma.mmminp'].search([('mmmexpordref', '=', pick.name), ('mmmres', 'not in', ['FIN'])])
                    for ulma_move in moves_ids:
                        index = int(ulma_move.mmmcod)
                        move_line = self.env['stock.move.line'].browse(index)
                        pick.move_line_ids[index].write({
                            'qty_done': ulma_move.mmmcanuni,
                            'ulma_state': 'P'
                        })
                    pick.write({
                        'ulma_state': 'P'
                    })
                return flag_type
        except Exception as error:                  
            raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)
    
    @api.multi
    def create_packages_for_ulma(self):
        for pick in self:
            try:
                if pick.move_line_ids:
                    abc_class = pick.move_line_ids.mapped("product_id").mapped("abc_classification")
                    for class_type in abc_class:
                        type_selecction_list = pick.move_line_ids.filtered(lambda x: x.product_id.abc_classification == class_type)
                        self.create_package_from_selection(type_selecction_list)          
            except Exception as error:                  
                raise UserError("Sorry! we found an error in your records, solve it and try again: %s" % error)
    
    @api.model
    def create_package_from_selection(self, type_selecction_list):
        if len(type_selecction_list) <= 8 and (len(type_selecction_list) % 2 == 0 or len(type_selecction_list) == 1):
            package_id = self.env['stock.quant.package'].create({
                'company_id': self.env.user.company_id,
                'location_id': type_selecction_list[0].picking_id.location_dest_id
            })

            for move_line in type_selecction_list:
                move_line.write({
                    'result_package_id': package_id.id
                })
        else:
            self.create_package_from_selection(type_selecction_list[0:8])
            self.create_package_from_selection(type_selecction_list[8:])



class StockMoveLine(models.Model):

    _inherit = "stock.move.line"
    ulma_state = fields.Selection([('W', 'En espera'), ('P', 'Procesado'), ('E', 'Error'), ('N', 'Not sent')], default='N')

