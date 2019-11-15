# -*- coding: utf-8 -*-

import base64

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    @http.route(['/my/picking/sign'], type='json', auth="public", website=True)
    def portal_picking_sign(self, res_id, access_token=None, partner_name=None, signature=None):
        img = signature
        pick = request.env['stock.batch.picking'].browse(res_id)
        if pick:
            pick.digital_signature = img


        return {'success': _('El albarán %s se ha firmado correctamente.'%pick.name),
                'redirect_url': "/web#model=%s&amp;id=%s&amp;action=%s&amp;view_type=form" % (pick._name, pick.id, 'report.client_action')}

