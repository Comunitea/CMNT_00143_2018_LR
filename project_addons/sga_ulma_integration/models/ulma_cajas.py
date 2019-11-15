# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
from odoo.exceptions import UserError

class UlmaCajas(models.Model):
    _name = "ulma.cajas"
    _description = "cajas from ULMA"
    _auto = False
    _table = "ulma_cajas"

    matricula = fields.Char()
    referencia = fields.Char()
    hueco = fields.Integer()
    cantidad = fields.Integer()
    tipo = fields.Char()
    caja_id = fields.Char()
    procesado = fields.Char()
    origen = fields.Char()
    confirmado = fields.Char()
    fecha = fields.Datetime()

    @api.multi
    def check_packages_from_adaia(self):
        packages = self.search([('confirmado', '=', 'C'), ('procesado', '=', 'N')])
        for package in packages:
            package_odoo = self.env['stock.quant.package'].search([('name', '=', package.matricula)])

            if package_odoo:
                if package.tipo.startswith('C') == 1:
                    location_dest_id = self.env['stock.location'].search_read([('ulma_type', '=', 'SUBUNI')], fields=['id'])
                else:
                    location_dest_id = self.env['stock.location'].search_read([('ulma_type', '=', 'SUBPAL')], fields=['id'])

                self.env['stock.picking'].transfer_package(package_odoo, package_odoo.location_id.id, location_dest_id)
                package.update({
                    'procesado': 'Y'
                })