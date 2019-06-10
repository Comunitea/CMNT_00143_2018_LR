# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    def get_apk_info(self):
        fields = ['id', 'name']

        vals = {}
        for f in fields:
            vals[f] = self[f]

        vals.update(self.update_info_route_vals())
        return vals

    @api.model
    def get_lines_info_apk(self, vals):

        ##Cambio por rendimiento

        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        lines = package_obj.move_line_ids

        move_lines_info = []
        for line in lines:
            move_lines_info.append(line.get_apk_info())
        
        data = {
            'move_lines_info': move_lines_info,
            'package_info': package_obj.get_apk_info()
            }

        
        return data
    
    @api.model
    def delete_package_from_apk(self, vals):
        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        domain = [('result_package_id', '=', package_id)]
        moves = self.env['stock.move'].search(domain)
        for move in moves:
            move.move_line_ids.update({
                'result_package_id': False
            })
        return package_obj.unlink()
            

    def get_package_vals(self, package_id):
        vals = {'shipping_type': self.shipping_type,
                }
        return vals


    @api.model
    def change_shipping_type(self, vals):
        package_id = vals.get('package', False)
        shipping_type = vals.get('shipping_type', False)
        carrier_id = vals.get('carrier_id', False)
        delivery_route_path_id = vals.get('delivery_route_path_id', False)

        vals = {
            'shipping_type': shipping_type,
            'carrier_id': carrier_id,
            'delivery_route_path_id': delivery_route_path_id
        }

        package_obj = self.env['stock.quant.package'].browse(package_id)
        package_obj.update(vals)

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

    def update_from_move_line(self, move_line):
        vals = move_line.move_id.update_info_route_vals()
        for pack in self:
            pack.write(vals)

    @api.model
    def update_object_from_apk(self, values):

        ctx = self._context.copy()
        ctx.update(write_from_package=True)
        print (values)
        package_id = self.browse(values.get('package_id', False))
        move_line_ids = self.env['stock.move.line'].browse(values.get('move_line_ids', False))
        action = values.get('action')
        move_line = self.env['stock.move.line'].search([('package_id', '=', self.id)])
        if action == 'new':
            move_line = self.env['stock.move.line'].search([('package_id', '=', self.id)])
            if move_line:
                result_package_id = self.create(move_line[0].update_info_route_vals())
                move_line.with_context(ctx).write({'result_package_id': result_package_id.id})

        elif action == 'unlink':
            move_line = self.env['stock.move.line'].search([('package_id', '=', self.id)])
            if move_line:
                move_line_ids.with_context(ctx).write({'result_package_id': False})

        else:
            result_package_id = self.env['stock.quant.package'].browse(values['result_package_id'])
            ##Si ya tienen moviemintos, entonces todos lo movimeitneos pasana tener info ruta del pack
            move_line = self.env['stock.move.line'].search([('package_id', '=', self.id)])
            if move_line:
                move_line_ids.with_context(ctx).write({'result_package_id': result_package_id})

        package_id.result_package_id = result_package_id
        return result_package_id.ids


    def update_to_new_package(self):
        move_line = self.env['stock.move.line'].search([('package_id', '=', self.id)])
        if move_line:
            new_pack = self.create(move_line[0].update_info_route_vals())
            move_line.write({'result_package_id': new_pack.id})
        return new_pack