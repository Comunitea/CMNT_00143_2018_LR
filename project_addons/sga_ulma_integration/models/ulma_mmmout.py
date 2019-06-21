# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
from odoo.exceptions import UserError

class UlmaMmmout(models.Model):
    _name = "ulma.mmmout"
    _description = "Movements sent to Ulma"
    _auto = False
    _table = "ulma_mmmout"

    mmmcmdref = fields.Char(string="mmmcmdref", default='SAL', max=9, NULL=False)
    mmmdisref = fields.Char(string="mmmdisref", max=9)
    mmmges = fields.Char(default='ULMA', max=9, NULL=False)
    mmmres = fields.Char(max=9)
    mmmsesid = fields.Integer(max=9)
    momcre = fields.Date()
    mmmartean = fields.Char(max=30)
    mmmbatch = fields.Char(max=9)
    mmmmomexp = fields.Date()
    mmmacccolcod = fields.Integer(max=9)
    mmmentdes = fields.Char(max=70)
    mmmexpordref = fields.Char(max=15)
    mmmterref = fields.Char(max=16)
    mmmentdir1 = fields.Char(max=70)
    mmmentdir2 = fields.Char(max=70)
    mmmentdir3 = fields.Char(max=70)
    mmmentdir4 = fields.Char(max=70)
    mmmurgnte = fields.Char(max=1)
    mmmtraref = fields.Char(max=16)
    mmmartdes = fields.Char(max=40)
    mmmartref = fields.Char(max=16)
    mmmcanuni = fields.Integer(max=9)
    mmmsecada = fields.Integer(max=9)
    mmmacccod = fields.Integer(max=9)
    mmmfeccad = fields.Date()
    mmmartapi = fields.Integer(default=0, max=1)
    mmmminudsdis = fields.Integer(max=9)
    mmmabclog = fields.Char(max=1)
    mmmdim = fields.Char(max=4)
    mmmcntdorref = fields.Char(max=18)
    mmmcrirot = fields.Char(max=20)
    mmmdorhue = fields.Char(max=1)
    mmmlot = fields.Char(max=20)
    mmmmomexp = fields.Date()
    mmmmonlot = fields.Char(max=1)
    mmmrecref = fields.Char(max=15)
    mmmubidesref = fields.Char(max=16)
    mmmzondesref = fields.Char(max=4)
    mmmobs = fields.Char(max=255)

    @api.model
    def create(self, vals):
        return super().create(vals)

