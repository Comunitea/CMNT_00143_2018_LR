# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class UlmaProcessedContainers(models.Model):
    _name = "ulma.processed.containers"
    _description = "containers from ADAIA to ULMA"

    matricula = fields.Char()
    tipo = fields.Char()
    package_id = fields.Many2one('stock.quant.package')

    @api.multi
    def check_packages_from_adaia(self):
        activated = self.env['ir.config_parameter'].get_param('sga_ulma_integration.ulma_activated', False)
        _logger.info("Comprobando si hay paquetes de ADAIA.")
        sql_select = "select matricula, tipo from ulma_cajas where confirmado = 'C' and procesado = 'N' and fecha > (NOW() - interval '1 day') group by matricula, tipo"
        self._cr.execute(sql_select)
        packages = self._cr.fetchall()

        _logger.info("Número de paquetes encontrados: {}.".format(len(packages)))
        for package in packages:
            _logger.info("Buscando paquete con matrícula: {}.".format(package[0]))
            package_odoo = self.env['stock.quant.package'].search([('name', '=', package[0])])
            
            if package_odoo:
                _logger.info("Actualizando paquete con matrícula: {}.".format(package_odoo.name))
                if package[1].startswith('C'):
                    _logger.info("Moviendo paquete {} con ID {} a cajas.".format(package_odoo.name, package_odoo.id))
                    location_dest_id = self.env['stock.location'].search_read([('ulma_type', '=', 'SUBUNI')], fields=['id'], limit=1)[0]["id"]
                else:
                    _logger.info("Moviendo paquete {} con ID {} a palés.".format(package_odoo.name, package_odoo.id))
                    location_dest_id = self.env['stock.location'].search_read([('ulma_type', '=', 'SUBPAL')], fields=['id'], limit=1)[0]["id"]
                print(location_dest_id)
                print(package_odoo)
                self.env['stock.picking'].transfer_package(package_odoo.id, location_dest_id)
                sql_update = "update ulma_cajas set ('procesado') values ('Y') where matricula = {}".format(package[0])
                self.create({
                    'matricula': package[0],
                    'tipo': 'Cajas' if package[1].startswith('C') else 'Palés',
                    'package_id': package_odoo.id
                })
                if activated:
                    _logger.info('Marco como procesado el contenedor/paquete {} ... '.format(package[0]))
                    self._cr.execute(sql_update)
                    done = self._cr.fetchall()
                    _logger.info('Ok')
                else:
                    _logger.info("Procesado paquete {} con ID {}.".format(package_odoo.name, package_odoo.id))