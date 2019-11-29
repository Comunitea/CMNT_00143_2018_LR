# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import json

from odoo import _, api, fields, exceptions, models
from odoo.tools.float_utils import float_compare
from requests import Session

from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)

try:
    from zeep import Client
    from zeep.transports import Transport
    from zeep.plugins import HistoryPlugin
except (ImportError, IOError) as err:
    _logger.debug(err)

try:
    from odoo.addons.queue_job.job import job
except ImportError:
    _logger.debug('Can not `import queue_job`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory



class StockMove(models.Model):
    _inherit = 'stock.move'

    check_availability_jobs_ids = fields.Many2many(
        comodel_name='queue.job', column1='incoming_move_id', column2='job_id',
        string="Connector Jobs", copy=False)

    @job(default_channel='root.move_check_availability')
    @api.multi
    def process_move_for_check_availability(self):
        self.check_availability_after_incoming()

    def _action_done(self):
        res = super()._action_done()
        res._process_move_for_check_availability()
        return res

    @api.multi
    def get_moves_to_check(self):
        return self.filtered(lambda x: x.location_dest_id == x.warehouse_id.lot_stock_id or x.location_dest_id in x.warehouse_id.lot_stock_id.child_ids)

    @api.multi
    def _process_move_for_check_availability(self):
        moves_to_check = self.filtered(lambda x: not x.move_dest_ids)
        queue_obj = self.env['queue.job'].sudo()
        for move in moves_to_check.get_moves_to_check():
            new_delay = move.sudo(move.create_uid).with_context(
                    company_id=move.company_id.id
                ).with_delay(
                    eta=2,
                ).process_move_for_check_availability()
            job = queue_obj.search([
                    ('uuid', '=', new_delay.uuid)
                ], limit=1)
            move.sudo(move.create_uid).check_availability_jobs_ids |= job

    def get_to_check_availability_domain(self):
        domain = [('location_id', 'child_of', self.warehouse_id.lot_stock_id.id), ('state', 'in', ('confirmed', 'partially_available')), ('product_id', '=', self.product_id.id)]
        return domain


    def get_to_check_availability_order(self):
        order ='date_expected asc'
        return order

    def get_to_check_availability_ordered(self):
        return self

    @api.multi
    def check_availability_after_incoming(self):
        ## todo revisar con varias compañias  ...... ###

        ctx = self._context.copy()
        company_id = self[0].company_id
        for move in self:
            user_id = move.create_uid
            ctx.update(force_company=company_id.id)
            move_id = move.sudo(user_id).with_context(ctx)
            domain = move_id.get_to_check_availability_domain()
            order = move_id.get_to_check_availability_order()
            moves_to_check = self.env['stock.move'].sudo(user_id).with_context(ctx).search(domain, order=order)
            move_id.get_to_check_availability_ordered(moves_to_check)._action_assign()