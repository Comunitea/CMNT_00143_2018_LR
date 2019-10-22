# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools

class UlmaMmminp(models.Model):
    _name = "ulma.mmminp"
    _description = "Movements from Ulma"
    _auto = False
    _table = "ulma_mmminp"
    
    mmmres = fields.Char(max=9)
    mmmges = fields.Char(default="ULMA", NULL=False, max=9)
    mmmcmdref = fields.Char(default='SAL', max=9, NULL=False)
    mmmexpordref = fields.Char(max=15)
    mmmsesid = fields.Integer(max=9)
    mmmacccolcod = fields.Integer(max=9)
    mmmresmsj = fields.Char(max=80)
    mmmcanuni = fields.Integer(max=9)
    mmmartref = fields.Char(max=16)
    momcre = fields.Datetime()

    @api.multi
    def check_on_create(self, record_id):
        res = self.browse(record_id)
        if res.mmmres == 'FIN':
            pick_obj = self.env['stock.picking'].search([('name', '=', res.mmmexpordref)])
            batch = self.env['stock.batch.picking'].browse(pick_obj.batch_picking_id.id)
            batch.get_from_ulma()