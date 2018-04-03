# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class MultiMoves(models.TransientModel):

	_name = "multi.moves"

	@api.multi
	def create_move(self):
		active_ids = self._context.get('active_ids')
		schedual_records = self.env['tenancy.rent.schedule'].search([('id', 'in', active_ids)])
		for record in schedual_records:
			if not record.move_id:
				move_line_obj = self.env['account.move.line']
				created_move_ids = []
				journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])
				
				depreciation_date = datetime.now()
				company_currency = record.tenancy_id.company_id.currency_id.id
				current_currency = record.tenancy_id.currency_id.id
				sign = -1
				move_vals = {
						'name': record.tenancy_id.name or False,
						'date': depreciation_date,
						'schedule_date': record.start_date,
						'journal_id': journal_ids and journal_ids.ids[0],
						'asset_id': record.tenancy_id.property_id.id or False,
						'source':record.tenancy_id.name or False,
						}
				move_id = self.env['account.move'].create(move_vals)
				# if not record.tenancy_id.property_id.income_acc_id.id:
				# 	raise Warning(_('Please Configure Income Account from Property in %s', % (record.tenancy_id.name)))
				move_line_obj.create({
								'name': record.tenancy_id.name,
								'ref': record.tenancy_id.ref,
								'move_id': move_id.id,
								'account_id': record.tenancy_id.property_id.income_acc_id.id or False,
								'debit': 0.0,
								'credit': record.tenancy_id.rent,
								'journal_id': journal_ids and journal_ids.ids[0],
								'partner_id': record.tenancy_id.tenant_id.parent_id.id or False,
								'currency_id': company_currency != current_currency and  current_currency or False,
								'amount_currency': company_currency != current_currency and - sign * record.tenancy_id.rent or 0.0,
								'date': depreciation_date,
								})
				move_line_obj.create({
								'name': record.tenancy_id.name,
								'ref': 'Tenancy Rent',
								'move_id': move_id.id,
								'account_id': record.tenancy_id.tenant_id.parent_id.property_account_receivable_id.id,
								'credit': 0.0,
								'debit': record.tenancy_id.rent,
								'journal_id': journal_ids and journal_ids.ids[0],
								'partner_id': record.tenancy_id.tenant_id.parent_id.id or False,
								'currency_id': company_currency != current_currency and  current_currency,
								'amount_currency': company_currency != current_currency and sign * record.tenancy_id.rent or 0.0,
								'analytic_account_id': record.tenancy_id.id,
								'date': depreciation_date,
								'asset_id': record.tenancy_id.property_id.id or False,
								})
				record.write({'move_id': move_id.id})
				created_move_ids.append(move_id.id)
				move_id.write({'ref': 'Tenancy Rent','state':'posted'})
			
			
