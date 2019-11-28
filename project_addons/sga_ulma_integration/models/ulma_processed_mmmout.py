# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class UlmaProcessedMmmout(models.Model):
    _name = "ulma.processed.mmmout"
    _description = "Movements sent to Ulma"

    mmmcmdref = fields.Char(string="mmmcmdref", default='SAL', max=9, NULL=False)
    mmmdisref = fields.Char(string="mmmdisref", max=9)
    mmmges = fields.Char(default='ULMA', max=9, NULL=False)
    mmmres = fields.Char(max=9)
    mmmsesid = fields.Integer(max=9)
    momcre = fields.Datetime()
    mmmartean = fields.Char(max=30)
    mmmbatch = fields.Char(string="Batch ID", max=9)
    mmmmomexp = fields.Datetime()
    mmmacccolcod = fields.Integer(string="Picking ID", max=9)
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
    mmmsecada = fields.Integer(string="Move line ID", max=9)
    mmmacccod = fields.Integer(max=9)
    mmmfeccad = fields.Datetime()
    mmmartapi = fields.Integer(default=0, max=1)
    mmmminudsdis = fields.Integer(max=9)
    mmmabclog = fields.Char(max=1)
    mmmdim = fields.Char(max=4)
    mmmcntdorref = fields.Char(max=18)
    mmmcrirot = fields.Char(max=20)
    mmmdorhue = fields.Char(max=1)
    mmmlot = fields.Char(max=20)
    mmmmonlot = fields.Char(max=1)
    mmmrecref = fields.Char(max=15)
    mmmubidesref = fields.Char(max=16)
    mmmzondesref = fields.Char(max=4)
    mmmobs = fields.Char(max=255)

    @api.model
    def create(self, vals):
        _logger.info("Creando nueva línea en MMMOUT.")
        print(vals)

        sql_update = "update ulma_mmmout set ('mmmcmdref', 'mmmdisref', 'mmmges', 'mmmres', 'mmmsesid', 'momcre', 'mmmartean', \
                'mmmbatch', 'mmmmomexp', 'mmmacccolcod', 'mmmentdes', 'mmmexpordref', 'mmmterref', 'mmmentdir1', 'mmmentdir2', \
                'mmmentdir3', 'mmmentdir4', 'mmmurgnte', 'mmmtraref', 'mmmartdes', 'mmmartref', 'mmmcanuni', 'mmmsecada', \
                'mmmacccod', 'mmmfeccad', 'mmmartapi', 'mmmminudsdis', 'mmmabclog', 'mmmdim', 'mmmcntdorref', 'mmmcrirot', \
                'mmmdorhue', 'mmmlot', 'mmmmonlot', 'mmmrecref', 'mmmubidesref', 'mmmzondesref', 'mmmobs') values \
                ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},\
                {}, {}, {}, {}, {})".format(vals['mmmcmdref'], vals['mmmdisref'], vals['mmmges'], vals['mmmres'], vals['mmmsesid'], \
                vals['momcre'], vals['mmmartean'], vals['mmmbatch'], vals['mmmmomexp'], vals['mmmacccolcod'], vals['mmmentdes'], \
                vals['mmmexpordref'], vals['mmmterref'], vals['mmmentdir1'], vals['mmmentdir2'], vals['mmmentdir3'], \
                vals['mmmentdir4'], vals['mmmurgnte'], vals['mmmtraref'], vals['mmmartdes'], vals['mmmartref'], \
                vals['mmmcanuni'], vals['mmmsecada'], vals['mmmacccod'], vals['mmmfeccad'], vals['mmmartapi'], \
                vals['mmmminudsdis'], vals['mmmabclog'], vals['mmmdim'], vals['mmmcntdorref'], vals['mmmcrirot'], \
                vals['mmmdorhue'], vals['mmmlot'], vals['mmmmonlot'], vals['mmmrecref'], \
                vals['mmmubidesref'], vals['mmmzondesref'], vals['mmmobs'])
        print(sql_update)
        #Descomentar cuando sea seguro probar
        self._cr.execute(sql_update)
        done = self._cr.fetchall()

        processed_vals = {
            'mmmcmdref': vals['mmmcmdref'],
            'mmmdisref': vals['mmmdisref'],
            'mmmges': vals['mmmges'],
            'mmmres': vals['mmmres'],
            'mmmsesid': vals['mmmsesid'],
            'momcre': vals['momcre'],
            'mmmartean': vals['mmmartean'],
            'mmmbatch': vals['mmmbatch'],
            'mmmmomexp': vals['mmmmomexp'],
            'mmmacccolcod': vals['mmmacccolcod'],
            'mmmentdes': vals['mmmentdes'],
            'mmmexpordref': vals['mmmexpordref'],
            'mmmterref': vals['mmmterref'],
            'mmmentdir1': vals['mmmentdir1'],
            'mmmentdir2': vals['mmmentdir2'],
            'mmmentdir3': vals['mmmentdir3'],
            'mmmentdir4': vals['mmmentdir4'],
            'mmmurgnte': vals['mmmurgnte'],
            'mmmtraref': vals['mmmtraref'],
            'mmmartdes': vals['mmmartdes'],
            'mmmartref': vals['mmmartref'],
            'mmmcanuni': vals['mmmcanuni'],
            'mmmsecada': vals['mmmsecada'],
            'mmmacccod': vals['mmmacccod'],
            'mmmfeccad': vals['mmmfeccad'],
            'mmmartapi': vals['mmmartapi'],
            'mmmminudsdis': vals['mmmminudsdis'],
            'mmmabclog': vals['mmmabclog'],
            'mmmdim': vals['mmmdim'],
            'mmmcntdorref': vals['mmmcntdorref'],
            'mmmcrirot': vals['mmmcrirot'],
            'mmmdorhue': vals['mmmdorhue'],
            'mmmlot': vals['mmmlot'],
            'mmmmonlot': vals['mmmmonlot'],
            'mmmrecref': vals['mmmrecref'],
            'mmmubidesref': vals['mmmubidesref'],
            'mmmzondesref': vals['mmmzondesref'],
            'mmmobs': vals['mmmobs']
        }
        return super().create(processed_vals)
        

