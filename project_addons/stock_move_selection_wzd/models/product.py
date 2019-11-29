# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manual_picking = fields.Boolean('Pick manual', help="Indica si se realiza un pick manual o realiza un flujo normal. Sale el listado en la orden de carga cuando proceda")