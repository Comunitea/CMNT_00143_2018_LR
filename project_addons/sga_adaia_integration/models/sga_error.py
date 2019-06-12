# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnologicos (<http://www.comunitea.com>)
# Kiko Sanchez (<kiko@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import codecs
IGNORED_CODES = ()

class SGAfileerror(models.Model):

    _name = "sga.file.error"

    sga_file_id = fields.Many2one('sga.file')

    file_name = fields.Char(string='Fichero', size=50)
    line_number = fields.Char('Linea')
    sga_operation = fields.Char("Operacion")
    object_type = fields.Char('Tipo de objeto', size=3)
    version = fields.Char('version')
    object_id = fields.Char("Id del objeto", size=50)
    error_code = fields.Char('Codigo de error')
    error_message = fields.Char("Mensaje de error")
    date_error = fields.Char('Fecha')
    ack = fields.Boolean("Ack", default=False)
    note = fields.Text("File line")
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Artículo')
    picking_id = fields.Many2one('stock.picking', string='Albarán')

    def confirm_ack(self):
        self.write({'ack': True})

    def refresh_sga_state(self, object_type, object_name, line):
        if object_type in ('PRE', 'SOR'):
            domain = [('name', '=', object_name)]
            sga_object = self.env['stock.picking'].search(domain)
            if sga_object:
                sga_object.message_post(body="Pick <em>%s</em> <b>Error en </b>.\n%s" % (sga_object.name, line))

