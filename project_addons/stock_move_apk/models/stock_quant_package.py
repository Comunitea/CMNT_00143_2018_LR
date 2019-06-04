# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    @api.model
    def get_lines_info_apk(self, vals):
        ##Cambio por rendimiento
        domain = [('result_package_id', '=',  vals['package'])]
        lines = self.env['stock.move.line'].search(domain)
        
        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        lines = package_obj.move_line_ids
        move_lines_info = []
        for line in lines:
            move_lines_info.append((line.id, line.product_id.name, line.ordered_qty))
        
        data = {
            'move_lines_info': move_lines_info,
            'package_info': {
                'name': package_obj.name,
                'info_str': package_obj.info_route_str or package_obj.shipping_type
            }
        }
        
        return data
    
    @api.model
    def delete_package_from_apk(self, vals):
        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        domain = [('result_package_id', '=', package_id)]
        move_line_ids = self.env['stock.move.line'].search(domain)
        for move_line in move_line_ids:
            move_line.update({
                'result_package_id': None
            })
        return package_obj.unlink()
    
    @api.model
    def get_partner_empty_packages(self, vals):
        partner_id = vals['dest_partner_id']
        domain = [
            ('dest_partner_id', '=', partner_id),
            ('move_line_ids', '=', False)]
        partner_empty_packages = self.env['stock.quant.package'].search(domain)
        partner_empty_packages_info = []
        for package in partner_empty_packages:
            partner_empty_packages_info.append((package.id, package.name, package.shipping_type, package.partner_shipping_type))
        return partner_empty_packages_info

    def get_package_vals(self, package_id):
        vals = {'shipping_type': self.shipping_type,
                }
        return vals


    @api.model
    def change_shipping_type(self, vals):
        package_id = vals['package']
        shipping_type = vals['shipping_type']

        package_obj = self.env['stock.quant.package'].browse(package_id)
        package_obj.update({
            'shipping_type': shipping_type
        })

        domain = [('result_package_id', '=', package_id)]
        move_line_ids = self.env['stock.move.line'].search(domain)

        ##saco vals de la función por claridad
        vals = package_obj.get_package_vals(package_id)
        move_line_ids.write(vals)
        #necesito escribir en los move.line y en los move para porder filtrar despues
        move_line_ids.mapped('move_id').write(vals)


        return True

    @api.model
    def create_new_package_from_move(self, vals):
        move_line_id = vals['move_line_id']
        line_id = self.env['stock.move.line'].browse(move_line_id)
        new_package = self.env['stock.quant.package'].create({
            'dest_partner_id': vals['dest_partner_id'],
            'shipping_type': line_id.move_id.shipping_type
        })
        if new_package.id:
            line_id.update({
                'result_package_id': new_package.id
            })
        return new_package.id
