# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from pprint import pprint

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    product_default_code = fields.Char(related="product_id.default_code")
    origin = fields.Char(related="move_id.origin")
    partner_id = fields.Many2one(related="move_id.partner_id")
    name = fields.Char(related="product_id.product_tmpl_id.name")
    partner_shipping_type = fields.Selection(related="move_id.partner_id.shipping_type")
    result_package_shipping_type = fields.Selection(related="result_package_id.shipping_type")


    def get_domain_for_apk_list(self, vals):
        
        partner_id = vals.get('partner_id', False)
        domain = [('location_dest_id.usage', '=', 'customer'),
                  ('state', 'in', ['assigned', 'partially_available']),
                  ('picking_id', '=', False)]
        if partner_id:
            domain +=[('move_id.partner_id', '=', partner_id)]

        return domain

    @api.model
    def get_stock_move_lines_list_apk(self, vals):

        domain = self.get_domain_for_apk_list(vals)
        move_lines = self.env['stock.move.line'].search(domain)
        pkg_list = move_lines.mapped('result_package_id')

        full_stock_moves = []
        current_partner_pkg_list = []
        current_partner_arrival_pkgs_list = []
        for move_line in move_lines:
            move_line_obj = {
                'id': move_line.id,
                'name': move_line.name,
                'origin': move_line.origin,
                'product_qty': move_line.product_qty,
                'shipping_type': move_line.shipping_type,
                'urgent': move_line.urgent,
                'isChecked': False
            }

            move_id = move_line.move_id

            if move_id.package_id and move_id.package_id.id:
                move_line_obj['package_id'] = {
                    'id': move_id.package_id.id,
                    'name': move_id.package_id.name
                }
                if move_line_obj['package_id'] not in current_partner_arrival_pkgs_list:
                    current_partner_arrival_pkgs_list.append(move_line_obj['package_id'])
            else:
                move_line_obj['package_id'] = False
            
            if move_id.result_package_id.id:
                move_line_obj['result_package_id'] = {
                    'id': move_id.result_package_id.id,
                    'name': move_id.result_package_id.name,
                    'shipping_type': move_id.result_package_id.shipping_type,
                    'urgent': move_id.result_package_id.urgent
                }
                if move_line_obj['result_package_id'] not in current_partner_pkg_list:
                    current_partner_pkg_list.append(move_line_obj['result_package_id'])
            else:
                move_line_obj['result_package_id'] = False

            full_stock_moves.append(move_line_obj)
        
        package_obj = self.env['stock.quant.package']
        empty_pkgs = package_obj.get_partner_empty_packages(vals)

        for pkg in empty_pkgs:
            pkg_data = {
                'id': pkg.id,
                'name': pkg.name,
                'shipping_type': pkg.shipping_type,
                'urgent': pkg.urgent
            }
            current_partner_pkg_list.append(pkg_data)
        
        res = {
            'move_lines': full_stock_moves,
            'result_package_ids': current_partner_pkg_list,
            'arrival_package_ids': current_partner_arrival_pkgs_list
        }
        
        return res


    @api.model
    def get_users_list_for_apk(self, vals):
        domain = self.env['stock.move.line'].get_domain_for_apk_list({})
        if len(self.env['stock.move'].search(domain)) > 0:
            partner_ids = self.env['stock.move'].search(domain).mapped('partner_id')
            partner_list = []
            for partner in partner_ids:
                partner_obj = {
                    'id': partner.id,
                    'name': partner.name,
                    'shipping_type': partner.shipping_type
                }
                partner_list.append(partner_obj)
            return partner_list
        else:
            partner_list = []
            return partner_list

    @api.model
    def toggle_urgent_option(self, vals):
        move_id = vals.get('id', False)
        urgent = vals.get('urgent', False)
        move_obj = self.browse(move_id)
        move_obj.update({
            'urgent': urgent
        })
        if move_obj.urgent == urgent:
            return True
        else:
            return False

    def update_to_new_package(self, new_package_ids):
        create = True
        for pack in new_package_ids:
            ok = pack.update_info_route_vals() == self.update_info_route_vals()
            if ok:
                self.move_id.write({'result_package_id': pack.id})
                pprint(self.move_id)
                create = False
                break

        if create:
            vals_0 = self.update_info_route_vals()
            new_result_package_id = self.env['stock.quant.package'].create(vals_0)
            pprint(self.move_id)
            self.move_id.write({'result_package_id': new_result_package_id.id})
            new_package_ids += new_result_package_id
        return new_package_ids