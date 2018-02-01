# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools import amount_to_text_en
import math


class ReportPaymentTransfer(models.AbstractModel):
    _name = 'report.mass_payment.report_transfer'

    def _get_amount_in_word(self, doc):
        amount_word = amount_to_text_en.amount_to_text(doc.amount, lang='en', currency=doc.journal_id.currency_id)
        # amount_word_new = amount_word.replace('Cent', '')
        if 'and Zero' in amount_word:
            new_amount_word = amount_word.replace('and Zero', '')
        else:
            new_amount_word = amount_word
        return new_amount_word

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # self.model = self.env.context.get('active_model')
        # doc = self.env[self.model].browse(self.env.context.get('active_id'))
        doc = self.env['account.payment'].browse(docids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'account.payment',
            'docs': doc,
            'data': data,
            'get_amount_in_word': self._get_amount_in_word(doc),
            # 'get_payment_total': self._get_payment_total(doc),
        }
        return Report.render('mass_payment.report_transfer', docargs)
