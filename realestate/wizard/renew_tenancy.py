# -*- encoding: utf-8 -*-

from datetime import datetime
from odoo.tools import misc
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class wizard_renew_tenancy(models.TransientModel):
	_name = 'renew.tenancy'

	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	rent_type_id = fields.Many2one('rent.type', 'Rent Type', required=True)


	@api.multi
	def renew_contract(self):
		"""
			This Button Method is used to Renew Tenancy.
		@param self: The object pointer
		@return: Dictionary of values.
		"""
		cr, uid, context = self.env.args
		context = dict(context)
		if context is None:
			context = {}
		modid = self.env['ir.model.data'].get_object_reference('realestate', 'property_analytic_view_form')
		if context.get('active_ids', []):
			for rec in self:
				start_d = datetime.strptime(rec.start_date, DEFAULT_SERVER_DATE_FORMAT).date()
				end_d = datetime.strptime(rec.end_date, DEFAULT_SERVER_DATE_FORMAT).date()
				if start_d > end_d:
					raise Warning(_('Please Insert End Date Greater Than Start Date'))
				act_prop = self.env['account.analytic.account'].browse(context['active_ids'])
				act_prop.write({
						'date_start' : rec.start_date,
						'date' : rec.end_date,
						'rent_type_id' : rec.rent_type_id and rec.rent_type_id.id or False,
						'state':'draft',
						'rent_entry_chck':False,
						})
		self.env.args = cr, uid, misc.frozendict(context)
		return {
			'view_mode': 'form',
			'view_id': modid[1],
			'view_type': 'form',
			'res_model': 'account.analytic.account',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id': context['active_ids'][0],
			}
