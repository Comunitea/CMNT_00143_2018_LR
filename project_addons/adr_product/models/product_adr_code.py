# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AdrCodeCategory(models.Model):
    _name = "adr.code.category"

    code = fields.Char('Code')
    x_kgrs_11363 = fields.Integer('x Kgrs', help ="For exception 1.1.3.6.3")
    x_kgrs_11364 = fields.Integer('x Kgrs', help ="For exception 1.1.3.6.4")


class AdrCodeRanking(models.Model):
    _name = "adr.code.ranking"

    code = fields.Char("Code")
    name = fields.Char('Name')



class ProductAdrCode(models.Model):

    _name = "product.adr.code"

    denomtecnica = fields.Char('ADR Descripction')
    peligroma = fields.Boolean('Dangerous')
    exe22315 = fields.Boolean ('22315 Exention')
    bultodesc = fields.Char("Package description")

    numero_onu = fields.Char('Name')
    official_name = fields.Char('Offical desc.')
    acc_signals = fields.Char('Access. signals')
    ranking_id = fields.Many2one('product.adr.code', 'Ranking')
    packing_group = fields.Char('Packing group')
    t_code = fields.Char("Tunnel code")
    qty_limit = fields.Integer('Qty limit')
    adr_category_id = fields.Many2one('adr.code.category', 'Category')


class AdrPackingList(models.Model):

    _name = "adr.packing.list"

    name = fields.Char('Name')
    delivered_date = fields.Datetime()
    picking_ids = fields.One2many('stock.picking')

