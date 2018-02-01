# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class CheckReportWizard(models.TransientModel):
    _name = 'check.report.wizard'

    @api.multi
    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        payments = self.env['account.payment'].browse(active_ids)
        datas = {
             'ids': active_ids,
             'model': 'account.payment',
             'form': self.read()[0]
        }
        return self.env['report'].get_action(payments, 'mass_payment.report_mass_payment', data=datas)
