# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    def get_apk_info(self):
        fields = ['id', 'name', 'info_route_str']

        vals = {}
        for f in fields:
            vals[f] = self[f]

        #vals['shipping_type'] = self._fields['shipping_type'].convert_to_export(self.shipping_type, self)
        vals['shipping_type'] = self.shipping_type

        if self.delivery_route_path_id:
            vals['delivery_route_id'] = {'id': self.delivery_route_path_id.id,
                                         'name': self.delivery_route_path_id.name}
        else:
            vals['delivery_route_id'] = {'id': False, 'name': ''}
        if self.carrier_id:
            vals['carrier_id'] = {'id': self.carrier_id.id,
                                  'name': self.carrier_id.name}
        else:
            vals['carrier_id'] = {'id': False, 'name': ''}

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
            'package_info': package_obj.get_apk_info(),
            'packaging_line_info': package_obj.get_packaging_lines({'package_id': package_id})
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
        values = {
            'shipping_type': vals.get('shipping_type', False),
            'delivery_route_path_id': vals.get('delivery_route_path_id', False),
            'carrier_id': vals.get('carrier_id', False)
        }

        ctx = self._context.copy()
        ctx.update(write_from_package=True)
        package_obj = self.env['stock.quant.package'].browse(package_id)
        package_obj.write(values)
        return True
    
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