# -*- coding: utf-8 -*-

from odoo import models, fields, api

class document_expiry_report(models.TransientModel):

	_name = 'document.expiry.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)

	@api.multi
	def open_document_expiry_tree(self):
		for data1 in self:
			data = data1.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_attachment_view_tree')[1]
			certificate_ids = self.env["property.attachment"].search([('expiry_date','>=',start_date),('expiry_date','<=',end_date)])
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'tree',
			'res_model': 'property.attachment',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context':self._context,
			'domain':[('id','in',certificate_ids.ids)],
			}

	@api.multi
	def print_report(self):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['start_date', 'end_date'])[0]
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'realestate.report_document_expiry', data=data)
