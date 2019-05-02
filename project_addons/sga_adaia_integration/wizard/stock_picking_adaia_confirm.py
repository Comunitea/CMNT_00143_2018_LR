# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnologicos (<http://www.comunitea.com>)
# Kiko Sanchez (<kiko@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, fields, models, _

class StockAdaiaConfirm(models.TransientModel):
    _name = 'stock.adaia.confirm'
    _description = 'Confirmación de Adaia'

    pick_id = fields.Many2one('stock.picking', "Pick a enviar")
    state = fields.Selection(related='pick_id.state', readonly=1)

    do_backorder = fields.Selection(related='pick_id.do_backorder')

    @api.model
    def default_get(self, fields):

        return super(StockAdaiaConfirm, self).default_get(fields)
        if not res['pick_id']:
            res['pick_id'] = self._context.get('active_id', False)
        return res

    @api.multi
    def process_force_and_send(self):
        self.ensure_one()
        self.pick_id.message_post(body=u"Env a Adaia<em>%s</em> <b>Forzado y envío </b>." % self.pick_id.name)

        if self.state == 'confirmed':
            self.pick_id.force_assign()

        if self.state == 'partially_available':
            self.pick_id.force_assign()

        if self.state == 'assigned':
            self.pick_id.new_adaia_file()

    @api.one
    def process_send(self):
        self.ensure_one()
        self.pick_id.message_post(body=u"Envío a Adaia<em>%s</em> <b>Envío</b>." % self.pick_id.name)
        self.pick_id.new_adaia_file(force=True)

    @api.one
    def process_force(self):
        self.ensure_one()
        self.pick_id.message_post(body=u"Envío a Adaia<em>%s</em> <b>Forzado</b>." % self.pick_id.name)
        self.pick_id.force_assign()

