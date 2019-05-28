# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError
from pprint import pprint


class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"

    ulma_integrated = fields.Boolean(related='picking_type_id.ulma_integrated')

    def send_to_ulma(self):
        for batch in self:
            for picking in batch.picking_ids:
                picking.send_to_ulma()

class StockPicking(models.Model):

    _inherit = "stock.picking"


    def _get_mmmouts(self):
        domain =[('mmmbatch', '=', self.name)]
        self.write({'ulma_ids': [(6,0, self.env['ulma.mmmout'].search(domain).ids)]})




    ulma_error = fields.Text(default="", string="Error msg in case the Ulma integration failed")
    ulma_integrated = fields.Boolean(related='picking_type_id.ulma_integrated')

    ulma_ids = fields.One2many('ulma.mmmout', compute=_get_mmmouts)



    def get_picking_ulma_vals(self):

        ### Modificar cuando se hagan entradas para hacer la misma función para entradas y salidas
        vals= {
            'mmmcmdref': "SAL",
            'mmmdisref': self.picking_type_id.ulma_type,
            'mmmges': "ULMA",
            'mmmres': "FINPED",
            'mmmsesid': 2 if self.picking_type_id.ulma_type == 'SUBPAL' else 1,
            'momcre': fields.datetime.now().date().strftime('%Y-%m-%d'),
            'mmmartean': "ean13",
            'mmmbatch': self.name,
            'mmmmomexp': self.date
        }
        return vals

    @api.multi
    def send_to_sga(self):
        to_ulma = self.filtered(lambda x: x.picking_type_id.ulma_integrated)
        for pick in to_ulma:
            cont = 0
            move_lines = pick.move_line_ids
            sale_ids = move_lines.mapped('move_id').mapped('sale_id')

            for sale in sale_ids:


                sale_moves = move_lines.filtered(lambda x: x.move_id.sale_id.id == sale.id)
                for move in sale_moves:
                    vals = move.get_move_line_ulma_vals(cont=cont)
                    ulma_move = self.env['ulma.mmmout'].create(vals)
                    cont += 1

                if ulma_move:
                    vals = sale.get_sale_to_ulma(pick, ulma_move, min(move.move_id.date_expected for move in sale_moves))
                    ulma_move = self.env['ulma.mmmout'].create(vals)
                sale_moves.write({'sga_state': 'PM'})
            vals = pick.get_picking_ulma_vals()
            self.env['ulma.mmmout'].create(vals)

        return super(StockPicking, self - to_ulma).send_to_sga()


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
                        'ulma_error': ulma_obj.mmmresmsj
                    })
                    flag_type = 1
                elif ulma_obj.mmmcmdref == 'SAL':
                    moves_ids = self.env['ulma.mmminp'].search([('mmmexpordref', '=', pick.name), ('mmmres', 'not in', ['FIN'])])
                    for ulma_move in moves_ids:
                        index = int(ulma_move.mmmcod)
                        move_line = self.env['stock.move.line'].browse(index)
                        pick.move_line_ids[index].write({
                            'qty_done': ulma_move.mmmcanuni,
                            'sga_state': 'P'
                        })
                    pick.write({
                        'sga_state': 'P'
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

