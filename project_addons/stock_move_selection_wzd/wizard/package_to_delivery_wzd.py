# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError
#
# class PackageToDeliveryWzd(models.TransientModel):
#
#     _name = 'package.to.delivery_wzd'
#
#     delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga')
#     package_ids = fields.Many2many('stock.quant.package', string="Paquetes en la línea")
#     move_line_ids = fields.Many2many('stock.move', compute="_get_move_line_ids", string="Artículos")
#     picking_ids = fields.Many2many('stock.picking')
#
#
#
