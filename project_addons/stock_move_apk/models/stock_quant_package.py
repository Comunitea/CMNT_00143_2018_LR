# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from pprint import pprint

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    @api.model
    def get_lines_info_apk(self, vals):
        ##Cambio por rendimiento
        domain = [('result_package_id', '=',  vals['package'])]
        lines = self.env['stock.move.line'].search(domain)
        
        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        lines = self.env['stock.move'].search([('result_package_id', '=', package_id)]).mapped('move_line_ids')
        move_lines_info = []
        for line in lines:
            line_data = {
                'id': line.id,
                'name': line.product_id.name,
                'ordered_qty': line.ordered_qty,
                'urgent': line.urgent
            }
            move_lines_info.append(line_data)
        
        data = {
            'move_lines_info': move_lines_info,
            'package_info': {
                'name': package_obj.name,
                'info_str': package_obj.info_route_str or package_obj.shipping_type,
                'urgent': package_obj.urgent
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
        partner_id = vals['partner_id']
        domain = [
            ('dest_partner_id', '=', partner_id),
            ('move_line_ids', '=', False)]
        partner_empty_packages = self.env['stock.quant.package'].search(domain)
        return partner_empty_packages
        

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
    
    @api.model
    def toggle_urgent_option(self, vals):
        pkg_id = vals.get('id', False)
        urgent = vals.get('urgent', False)
        pkg_obj = self.browse(pkg_id)
        pkg_obj.update({
            'urgent': urgent
        })
        lines = self.env['stock.move'].search([('result_package_id', '=', pkg_id)]).mapped('move_line_ids')
        for line in lines:
            vals = {'id': line.id, 'urgent': urgent}
            result = self.env['stock.move.line'].toggle_urgent_option(vals)
        if pkg_obj.urgent == urgent:
            return True
        else:
            return False


    @api.multi
    def write(self, vals):
        return super().write(vals)

    @api.model
    def update_to_new_package_from_apk(self, values):
        ctx = self._context.copy()
        ctx.update(write_from_package=True)
        move_line_ids = self.env['stock.move.line'].browse(values['move_line_ids'])
        action = values.get('action')
        package_ids = self.env['stock.quant.package']
        if action == 'new':
            for line in move_line_ids:
                package_ids = line.with_context(ctx).update_to_new_package(package_ids)

        elif action == "new_partner_pack":
            partner_id = self.env['res.partner'].browse[(values.get('partner_id'))]
            vals_0 = partner_id.update_info_route_vals()
            new_result_package_id = self.env['stock.quant.package'].create(vals_0)
            package_ids += new_result_package_id

        elif action == 'unlink':
            move_line_ids.mapped('move_id').with_context(ctx).write({'result_package_id': False})

        else:
            package_ids = self.env['stock.quant.package'].browse(values['result_package_id'])
            ##Si ya tienen movimientos, entonces todos lo movimientos pasan a tener info ruta del pack
            if package_ids.move_line_ids:
                move_vals = {'result_package_id': package_ids.id}
                move_vals.update(package_ids.update_info_route_vals())
                move_line_ids.mapped('move_id').with_context(ctx).write(move_vals)
            else:
                for line in move_line_ids:
                    line.write({'result_package_id': package_ids.id})

        return package_ids.ids