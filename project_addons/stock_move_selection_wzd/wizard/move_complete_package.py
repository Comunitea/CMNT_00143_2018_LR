# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class MoveCompletePackageWzd(models.TransientModel):
    _name = 'move.complete.package.wzd'


    package_id = fields.Many2one('stock.quant.package', 'Paquete que moveremos')
    location_dest_id = fields.Many2one('stock.location', 'Ubicación de destino')
    auto_transfer = fields.Boolean('Validación automática', default=True)
    unpack = fields.Boolean('Desempaquetar al mover', default=False)

    @api.model
    def default_get(self, fields):

        defaults = super().default_get(fields)

        if self._context.get('active_id'):
            defaults.update({'package_id': self._context.get('active_id')})
        if self._context.get('location_dest_id'):
            defaults.update({'location_dest_id': self._context.get('location_dest_id')})

        return defaults

    @api.multi
    def move_package(self):
        package = self.package_id.id
        location_dest_id = self.location_dest_id.id
        auto = self.auto_transfer
        unpack = self.unpack
        picking_id = self.env['stock.picking'].transfer_package(package, location_dest_id, auto, unpack)
        action = picking_id.get_formview_action()
        return action