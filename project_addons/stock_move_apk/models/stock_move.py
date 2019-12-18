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

    @api.model
    def update_object_from_apk(self, values):
        ctx = self._context.copy()
        ctx.update(write_from_package=True)
        move_line_ids = self.env['stock.move.line'].browse(values['move_line_ids'])
        action = values.get('action', '')
        package_ids = self.env['stock.quant.package']

        if action == 'new':
            for line in move_line_ids:
                package_ids = line.with_context(ctx).update_to_new_package(package_ids)

        elif action == 'unlink':
            move_line_ids.mapped('move_id').with_context(ctx).write({'result_package_id': False})

        elif action == "new_partner_pack":
            partner_id = self.env['res.partner'].browse[(values.get('partner_id'))]
            vals_0 = partner_id.update_info_route_vals()
            new_result_package_id = self.env['stock.quant.package'].create(vals_0)
            package_ids += new_result_package_id

        else:
            package_ids = self.env['stock.quant.package'].browse(values['result_package_id'])
            ##Si ya tienen moviemintos, entonces todos lo movimeitneos pasana tener info ruta del pack
            if package_ids.move_line_ids:
                move_vals = {'result_package_id': package_ids.id}
                move_vals.update(package_ids.update_info_route_vals())
                move_line_ids.mapped('move_id').with_context(ctx).write(move_vals)
            else:
                for line in move_line_ids:
                    line.write({'result_package_id': package_ids.id})

        return package_ids.ids


    def get_domain_for_apk_list(self, vals):
        
        partner_id = vals.get('partner_id', False)
        domain = [('location_dest_id.usage', '=', 'customer'),
                  ('state', 'in', ['assigned', 'partially_available']),
                  ]
        if partner_id:
            domain += [('move_id.partner_id', '=', partner_id)]

        return domain

    def get_apk_info(self):
        fields = ['id', 'name', 'origin', 'product_qty', 'info_route_str']

        vals ={}
        for f in fields:
            vals[f] = self[f]

        vals['isChecked'] = False
        if self.package_id:
            vals['package_id'] = self.package_id.get_apk_info()
        if self.result_package_id:
            vals['result_package_id'] = self.result_package_id.get_apk_info()

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
    def get_apk_info_full(self, vals):


        domain = self.get_domain_for_apk_list(vals)
        move_lines = self.env['stock.move.line'].search(domain)

        full_stock_moves = []
        current_partner_pkg_list = []
        current_partner_arrival_pkgs_list = []

        for move_line in move_lines:
            full_stock_moves.append(move_line.get_apk_info())


        package_ids = move_lines.mapped('package_id')
        for pack in package_ids:
            current_partner_arrival_pkgs_list.append(pack.get_apk_info())

        result_package_ids = move_lines.mapped('result_package_id')
        for pack in result_package_ids:
            current_partner_pkg_list.append(pack.get_apk_info())

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
    def get_users_list_for_apk_from_search_box(self, vals):

        domain = self.env['stock.move.line'].get_domain_for_apk_list({})
        name = vals.get('name', False)
        if name:
            domain +=[('partner_id.name', 'ilike', name)]

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
    def assign_package(self, vals):
        return
        result_package_id = vals.get('result_package_id', False)
        move_ids = vals.get('move_line_ids', False)
        move_line_ids = self.browse(move_ids)
        move_ids = move_line_ids.mapped('move_id')
        return move_ids.assign_package(result_package_id)

    def update_to_new_package(self, new_package_ids):
        create = True
        for pack in new_package_ids:
            self.move_id.write({'result_package_id': pack.id})
            create = False
            break
        if create:
            vals_0 = self.update_info_route_vals()
            new_result_package_id = self.env['stock.quant.package'].create(vals_0)
            self.move_id.write({'result_package_id': new_result_package_id.id})
            new_package_ids += new_result_package_id
        return new_package_ids

    @api.model
    def change_shipping_type(self, vals):

        move_line_id = vals.get('move_line', False)
        values = {
            'shipping_type': vals.get('shipping_type', False),
            'delivery_route_path_id': vals.get('delivery_route_path_id', False),
            'carrier_id': vals.get('carrier_id', False)
        }
        move_line = self.browse(move_line_id)
        ctx = self._context.copy()
        ctx.update(write_from_package=True)
        move_line.move_id.write(vals)
        return True
