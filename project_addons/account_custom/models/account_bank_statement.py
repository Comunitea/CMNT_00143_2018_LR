# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, counterpart_aml_dicts=None,
                               payment_aml_rec=None, new_aml_dicts=None):
        if counterpart_aml_dicts:
            for aml_dict in counterpart_aml_dicts:
                if aml_dict['move_line'].ref:
                    aml_dict['name'] = aml_dict['name'] + " : " \
                                       + aml_dict['move_line'].ref

        return super().process_reconciliation(
                                counterpart_aml_dicts=counterpart_aml_dicts,
                                payment_aml_rec=payment_aml_rec,
                                new_aml_dicts=new_aml_dicts)
