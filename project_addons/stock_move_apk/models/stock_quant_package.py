# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    dest_partner_id = fields.Many2one("res.partner")
    delivery_carrier_id = fields.Many2one("delivery.carrier")
    selected_route = fields.Many2one("stock.location.route")
    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado."
    )
    partner_default_shipping_type = fields.Selection(related="dest_partner_id.default_shipping_type")

    @api.model
    def get_lines_info_apk(self, vals):
        package_id = vals['package']
        package_obj = self.env['stock.quant.package'].browse(package_id)
        lines = package_obj.move_line_ids
        move_lines_info = []
        for line in lines:
            move_lines_info.append((line.id, line.product_id.name, line.ordered_qty))
        return move_lines_info
    
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
            partner_empty_packages_info.append((package.id, package.name, package.shipping_type, package.partner_default_shipping_type))
        return partner_empty_packages_info

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
        for move_line in move_line_ids:
            move_line.update({
                'shipping_type': shipping_type
            })

        return True
