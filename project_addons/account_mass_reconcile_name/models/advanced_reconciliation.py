# Copyright 2013-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, models


class MassReconcileAdvancedName(models.TransientModel):

    _name = 'mass.reconcile.advanced.name'
    _inherit = 'mass.reconcile.advanced'

    @api.multi
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get('name') and
                    move_line.get('partner_id'))

    @api.multi
    def _matchers(self, move_line):
        return (('partner_id', move_line['partner_id']),
                ('name', move_line['name'].lower().strip()))

    @api.multi
    def _opposite_matchers(self, move_line):
        yield ('partner_id', move_line['partner_id'])
        yield ('name', (move_line['name'] or '').lower().strip())


