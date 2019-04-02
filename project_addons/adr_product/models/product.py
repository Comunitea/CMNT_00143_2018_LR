# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"


    adr_esadr = fields.Boolean('ADR', default=False, help = "Is ADR")
    adr_idnumonu = fields.Many2one('product.adr.code', 'ADR Code')
    adr_denomtecnica = fields.Char('ADR Descripction')
    adr_peligroma = fields.Boolean('Dangerous')
    adr_exe22315 = fields.Boolean ('22315 Exention')
    adr_bultodesc = fields.Char("Package description")



