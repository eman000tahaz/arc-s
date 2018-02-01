# -*- coding: utf-8 -*-

from openerp import api, fields, models


class Output(models.TransientModel):
    _name = 'v.excel.output'
    _description = 'Excel Report Output'

    name = fields.Char('File Name', size=256, readonly=True)
    filename = fields.Binary('File to Download', readonly=True)
    extension = fields.Char('Extension', default='xls')

    @api.multi
    def download(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/document?model=%s&field=filename&id=%s&filename=%s.%s' % (self._name, self.id, self.name, self.extension),
            'target': 'self'
        }
