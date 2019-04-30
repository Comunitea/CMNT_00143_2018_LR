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
    max_weight_11363 = fields.Integer('Max. Kg', help='Maximum amount allowed in one shipping for exception 1.1.3.6.3')
    max_weight_11364 = fields.Integer('Max. Kg', help='Maximum amount allowed in one shipping for exception 1.1.3.6.4')


class AdrCodeRanking(models.Model):
    _name = "adr.code.ranking"

    code = fields.Char("Code")
    name = fields.Char('Name')



class ProductAdrCode(models.Model):

    _name = "product.adr.code"

    denomtecnica = fields.Char('Denominación técnica')
    peligroma = fields.Boolean('Artículo peligroso')
    exe22315 = fields.Boolean ('Sujeto a la exención 22315')
    bultodesc = fields.Char("Descripción del bulto")

    numero_onu = fields.Char('Nombre')
    official_name = fields.Char('Descripción oficial')
    acc_signals = fields.Char('Señales accesorias')
    ranking_id = fields.Many2one('adr.code.ranking', 'Clasificación')
    packing_group = fields.Char('Grupo de embalaje')
    t_code = fields.Char("Código tunel")
    qty_limit = fields.Integer('Cantidad limitada')
    adr_category_id = fields.Many2one('adr.code.category', 'Categoría')
    multiplier = fields.Integer('Multiplicador categoría 1', help="Multiplicador aplicable para artículos de la categoría 1 en caso de producirse la exención 11363.")


class AdrPackingList(models.Model):

    _name = "adr.packing.list"

    name = fields.Char('Name')
    delivered_date = fields.Datetime()
    picking_ids = fields.One2many('stock.picking', 'adr_packing_list')

