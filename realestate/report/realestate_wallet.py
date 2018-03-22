# -*- coding: utf-8 -*-

import time
from odoo import api, models

class ReportRealestateWallet(models.AbstractModel):
	_name = 'report.realestate.report_realestate_wallet'

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		wallet_id = data['form'].get('wallet_id')
			
		wallet = self.env['realestate.wallet'].search([('id', '=', wallet_id[0])])
		records = self.env['account.asset.asset'].search([('wallet_id', '=', wallet_id[0])])

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'wallet': wallet,
			'records': records,
		}
		return self.env['report'].render('realestate.report_realestate_wallet', docargs)


