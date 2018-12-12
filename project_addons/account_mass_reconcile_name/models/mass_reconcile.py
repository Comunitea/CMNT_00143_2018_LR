# Copyright 2013-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, models


class AccountMassReconcileMethod(models.Model):

    _inherit = 'account.mass.reconcile.method'

    @api.model
    def _get_reconcilation_methods(self):
        methods = super(AccountMassReconcileMethod, self)._get_reconcilation_methods()
        methods += [
            ('mass.reconcile.advanced.name',
             'Advanced. Partner and Description.'),
        ]
        return methods