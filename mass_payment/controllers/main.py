# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
import base64


class Binary(http.Controller):

    @http.route('/web/binary/document', type='http', auth="public")
    @serialize_exception
    def download_document(self, model, field, id, filename=None, **kw):
        """Download link for excel files stored as binary fields."""
        record = request.env[model].browse([int(id)])
        res = record.read([field])[0]
        filecontent = base64.b64decode(res.get(field) or '')
        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
            return request.make_response(
                        filecontent,
                        [('Content-Type', 'application/octet-stream'),
                         ('Content-Disposition', content_disposition(filename))])
