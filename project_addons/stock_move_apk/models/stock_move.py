# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    product_default_code = fields.Char(related="product_id.default_code")
    origin = fields.Char(related="move_id.origin")
    partner_id = fields.Many2one(related="move_id.partner_id")
    name = fields.Char(related="product_id.product_tmpl_id.name")
    partner_default_shipping_type = fields.Selection(related="move_id.partner_id.default_shipping_type")
    result_package_shipping_type = fields.Selection(related="result_package_id.shipping_type")
    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado.",
    )

    @api.model
    def get_stock_move_lines_list_apk(self, vals):
        location_dest_id = vals['location_dest_id']
        partner_id = vals['partner_id']

        domain = [('location_dest_id', '=', location_dest_id), ('state', 'in', ['done']), ('move_dest_ids.move_line_ids.state', 'in', ['assigned']), ('move_dest_ids.move_line_ids.move_id.partner_id', '=', partner_id)]
        move_lines = self.env['stock.move'].search(domain).mapped('move_dest_ids').mapped('move_line_ids')
        pkg_list = move_lines.mapped('result_package_id')
        arrival_pkgs_list = move_lines.mapped('package_id.id')

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
                'partner_default_shipping_type': move_line.partner_default_shipping_type
            }

            if move_line.package_id.id:
                move_line_obj['package_id'] = {
                    '0': move_line.package_id.id,
                    '1': move_line.package_id.name
                }
                if move_line_obj['package_id'] not in current_partner_arrival_pkgs_list:
                    current_partner_arrival_pkgs_list.append(move_line_obj['package_id'])
            else:
                move_line_obj['package_id'] = False
            
            if move_line.result_package_id.id:
                move_line_obj['result_package_id'] = {
                    '0': move_line.result_package_id.id,
                    '1': move_line.result_package_id.name,
                    '2': move_line.result_package_id.shipping_type,
                    '3': move_line.result_package_id.dest_partner_id.default_shipping_type
                }
                if move_line_obj['result_package_id'] not in current_partner_pkg_list:
                    current_partner_pkg_list.append(move_line_obj['result_package_id'])
            else:
                move_line_obj['result_package_id'] = False

            full_stock_moves.append(move_line_obj)
        
        res = {
            'move_lines': full_stock_moves,
            'result_package_ids': current_partner_pkg_list,
            'arrival_package_ids': current_partner_arrival_pkgs_list
        }
        
        return res

                
class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def get_users_list_for_apk(self, vals):
        location_dest_id = vals['location_dest_id']
        
        domain = [('location_dest_id', '=', location_dest_id), ('state', 'in', ['done']), ('move_dest_ids.move_line_ids.state', 'in', ['assigned'])]
        if len(self.env['stock.move'].search(domain)) > 0:
            partner_ids = self.env['stock.move'].search(domain).mapped('move_dest_ids').mapped('move_line_ids').mapped('move_id').mapped('partner_id')
            partner_list = []
            for partner in partner_ids:
                partner_obj = {
                    '0': partner.id,
                    '1': partner.name,
                    '2': partner.default_shipping_type
                }
                partner_list.append(partner_obj)
            return partner_list
        else:
            partner_list = []
            return partner_list