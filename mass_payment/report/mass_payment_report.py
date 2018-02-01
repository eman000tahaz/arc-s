# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools import amount_to_text_en
import math


class ReportMassPayment(models.AbstractModel):
    _name = 'report.mass_payment.report_mass_payment'

    def _get_payment_approver(self):
        payment_approver = self.env.user.company_id.payment_approver_id
        return payment_approver

    def _get_payment_total(self, rec):
        subtotal = 0.0
        less_total = 0.0
        total = 0.0
        for line in rec.invoice_payment_id:
            subtotal += line.payment_amount

        for line in rec.payment_line_ids:
            if rec.partner_type == 'customer' and line.type == 'dr':
                less_total += line.amount
            elif rec.partner_type == 'supplier' and line.type == 'cr':
                less_total += line.amount
        total = subtotal - less_total
        amount_word = amount_to_text_en.amount_to_text(math.floor(total), lang='en', currency='')
        amount_word_new = amount_word.replace('Cent', '')
        if 'and Zero' in amount_word_new:
            new_amount_word = amount_word_new.replace('and Zero', '')
        else:
            new_amount_word = amount_word_new
        res = {'subtotal': subtotal, 'less_total': less_total, 'total': total, 'amount_word': new_amount_word}
        return res

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # self.model = self.env.context.get('active_model')
        # doc = self.env[self.model].browse(self.env.context.get('active_id'))
        doc = self.env['account.payment'].browse(docids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'account.payment',
            # 'data': data['form'],
            'docs': doc,
            'get_payment_approver': self._get_payment_approver(),
            'get_payment_total': self._get_payment_total(doc),
        }
        return Report.render('mass_payment.report_mass_payment', docargs)
