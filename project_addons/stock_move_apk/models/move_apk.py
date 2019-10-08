# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMoveApk(models.Model):
    _name = 'stock.move.apk'

    name = fields.Char(string='Move Apk', index=True, required=False,
                       help="An internal identification of the stock move apk")

    # Methods to open the POS
    @api.multi
    def open_ui(self):
        assert len(self.ids) == 1, "You can open only one session at a time"
        return {
            'type': 'ir.actions.act_url',
            'url': '/stock_move_apk/static/www/index.html',
            'target': 'self',
        }