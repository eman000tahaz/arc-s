# -*- coding: utf-8 -*-


from odoo import models, fields, api


class safety_certificate_report(models.TransientModel):

	_name = 'safety.certificate.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)

	@api.multi
	def open_certificate_expiry_tree(self):
		for data1 in self:
			data = data1.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_certificate_view_tree')[1]
			certificate_ids = self.env['property.safety.certificate'].search([('expiry_date','>=',start_date),('expiry_date','<=',end_date)])
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'tree',
			'res_model': 'property.safety.certificate',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context':self._context,
			'domain':[('id','in',certificate_ids.ids)],
			}

	@api.multi
	def print_report(self):
		if self._context is None:
			self._context = {}
		data = {
			'ids': self.ids,
			'model': 'account.asset.asset',
			'form': self.read(['start_date', 'end_date'])[0]
		}
		return self.env['report'].get_action(self, 'realestate.report_safety_certificate',
											 data=data)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: