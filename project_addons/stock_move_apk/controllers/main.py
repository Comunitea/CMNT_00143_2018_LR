# -*- coding: utf-8 -*-
import logging

from openerp import http

_logger = logging.getLogger(__name__)


class ProductionAppController(http.Controller):

    @http.route(['/packageApp/'], type='http', auth='public')
    def a(self, debug=False, **k):
        return http.local_redirect(
            '/stock_move_apk/static/www/index.html')

    @http.route(['/packageWww/'], type='http', auth='public')
    def a(self, debug=False, **k):
        return http.local_redirect(
            '/stock_move_apk/static/www_apk/index.html')
