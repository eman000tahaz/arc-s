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

		gross_values = []

		for record in records:
			gross_value = 0
			gross_value += record.value
			first_children = self.env['account.asset.asset'].search([('parent_id', '=', record.id)])
			for first_child in first_children:
				gross_value += first_child.value
				second_children = self.env['account.asset.asset'].search([('parent_id', '=', first_child.id)])
				for second_child in second_children:
					gross_value += second_child.value

			gross_values.append(gross_value)

		no = len(gross_values)

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'wallet': wallet,
			'records': records,
			'no': no,
			'gross_values': gross_values,
		}
		return self.env['report'].render('realestate.report_realestate_wallet', docargs)


