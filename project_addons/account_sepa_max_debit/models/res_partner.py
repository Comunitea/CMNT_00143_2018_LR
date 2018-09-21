# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from datetime import date
#from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ResPartner(models.Model):

    _inherit = 'res.partner'

    sepa_max_debit = fields.Float('Maximum Debit Receipt',
                                  company_dependent=True)

