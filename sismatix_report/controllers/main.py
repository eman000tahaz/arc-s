# -*- coding: utf-8 -*-
from odoo.http import Controller, route, request
import json
import odoo.http as http
from odoo.http import request
from odoo.addons.web.controllers.main import ExcelExport


class ReportView(Controller):
    @http.route('/web/download/pdf_view', type='http', auth='user')
    def print_pdf_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        s_data = {}
        s_data['form'] = {'model': model, 'rows': rows, 'fields': columns_headers}


        pdf = request.env['report'].get_pdf([1, 2], 'sismatix_report.report_sismatix', data=s_data)

        
        return request.make_response(pdf,
            # self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="'+str(model)+'.pdf"'),
                ('Content-Type', 'application/pdf')
            ],
            cookies={'fileToken': token}
        )

class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
