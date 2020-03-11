# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def compute_package_to_load_ids(self):
        for type in self.filtered('visible_package'):
            domain = [('state_progress', '=', 'preparation')]
            type.package_to_load_ids = self.env['stock.quant.package'].search(domain)
            type.count_package_to_load_ids = len(type.package_to_load_ids)
            domain = [('state_progress', 'in', ('loading', 'preparation'))]
            type.count_package_loaded_ids = self.env['stock.quant.package'].search_count(domain)
            if type.count_package_loaded_ids:
                type.rate_unloaded = (type.count_package_to_load_ids/type.count_package_loaded_ids) * 100
            else:
                type.rate_unloaded = 0.00


    package_to_load_ids = fields.One2many('stock.quant.package', string='Paquetes para cargar', compute="compute_package_to_load_ids")
    count_package_to_load_ids = fields.Integer('# Paquetes para cargar',
                                          compute="compute_package_to_load_ids")
    count_package_loaded_ids = fields.Integer('# Paquetes cargados',
                                               compute="compute_package_to_load_ids")
    visible_package = fields.Boolean('Paquetes en preparación')
    rate_unloaded = fields.Integer(compute='compute_package_to_load_ids', string="Ratio")


    def get_action_tree(self):
        if self._context.get('dest_model', 'stock.move') == 'stock.quant.package':
            action = self.env.ref(
                'stock_quant_package_wzd.action_sqp_tree').read()[0]
            domain = [('state_progress', '=', 'preparation')]
            action['domain'] = domain
            return action
        return super().get_action_tree()
