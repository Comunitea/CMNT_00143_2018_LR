# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError

class StockBatchPicking(models.Model):

    _inherit = "stock.batch.picking"

    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')

    def send_to_ulma(self):
        for batch in self:
            for picking in batch.picking_ids:
                picking.send_to_ulma()

class StockPicking(models.Model):

    _inherit = "stock.picking"

    def show_ulma_mmmout(self):
        tree = self.env.ref('sga_ulma_integration.ulma_mmmout_tree', False)
        action = self.env.ref(
            'sga_ulma_integration.action_ulma_mmmout_view').read()[0]
        action['domain'] = [('mmmbatch', '=', self.name)]
        action['views'] = [(tree and tree.id or False, 'tree'), (False, 'form')]
        return action

    ulma_error = fields.Text(default="", string="Error msg in case the Ulma integration failed")
    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    sga_integration_type = fields.Selection(related="picking_type_id.sga_integration_type")


    def get_picking_ulma_vals(self):
        vals = self.picking_type_id.get_ulma_vals('pick')
        update_vals= {
            'momcre': fields.datetime.now().date().strftime('%Y-%m-%d'),
            'mmmbatch': self.name,
            'mmmmomexp': self.date
        }
        vals.update(update_vals)
        return vals

    def force_button_validate(self):
        self.sga_state = 'SR'
        return self.button_validate()
    
    def move_to_not_sent(self):
        self.sga_state = 'NE'

    @api.multi
    def send_to_sga(self):
        to_ulma = self.filtered(lambda x: x.picking_type_id.sga_integrated and self.state == 'assigned')
        ulma_out = self.env['ulma.mmmout']
        for pick in to_ulma:
            ##ulma_out.search([('mmmbatch', '=', self.name)]).unlink()
            cont = 0
            move_lines_ids = pick.move_line_ids
            move_lines = pick.move_lines
            sale_ids = move_lines.mapped('sale_id')

            for sale in sale_ids:
                sale_moves = move_lines_ids.filtered(lambda x: x.move_id.sale_id.id == sale.id)
                for move in sale_moves:
                    vals = move.get_move_line_ulma_vals(cont=cont)
                    ulma_move = ulma_out.create(vals)
                    cont += 1
                    move.sga_state='PS'

                if ulma_move:
                    vals = sale.get_sale_to_ulma(pick, ulma_move, min(move.move_id.date_expected for move in sale_moves))
                    ulma_move = ulma_out.create(vals)


            vals = pick.get_picking_ulma_vals()
            ulma_out.create(vals)
            for move in move_lines:
                move.sga_state = pick.picking_type_id.get_parent_state(move.move_line_ids)
            pick.sga_state = pick.picking_type_id.get_parent_state(move_lines)

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
                        index = int(ulma_move.id)
                        move_line = self.env['stock.move.line'].browse(index)
                        if pick.move_line_ids[index] == ulma_move.mmmcanuni:
                            if pick.move_line_ids[index] != ulma_move.mmmcanuni:
                                pick.move_line_ids[index]._set_quantity_done(ulma_move.mmmcanuni)
                            else:
                                actual_move = self.env['stock.move'].search([('origin_returned_move_id', '=', move_line_ids[index].move_id.id)])
                                actual_move._prepare_move_line_vals(ulma_move.mmmcanuni)
                        
                        else:
                            diference = pick.move_line_ids[index].ordered_qty - ulma_move.mmmcanuni
                            pick.move_line_ids[index].move_id._split(diference)
                            pick.move_line_ids[index]._set_quantity_done(ulma_move.mmmcanuni)
                            pick.move_line_ids[index].write({
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

