# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
from odoo.exceptions import UserError

class UlmaPackinglist(models.Model):
    _name = "ulma.packinglist"
    _description = "packinglist from ULMA"
    _auto = False
    _table = "ulma_packinglist"

    mmmexpordref = fields.Char(max=15)
    estado = fields.Char(max=1)
    mmmsesid = fields.Integer(max=9)
    mmmbatch = fields.Integer(max=9)
    status = fields.Char(max=1)
    mmmres = fields.Char(max=9)
    mmmcmdref = fields.Char(max=9)