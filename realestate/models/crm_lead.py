# -*- coding: utf-8 -*-

import time
from odoo.exceptions import Warning, except_orm
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class crm_lead(models.Model):
	_inherit = "crm.lead"


	facing = fields.Char('Facing')
	demand = fields.Boolean('Is Demand')
	max_price = fields.Float('Max Price')
	min_price = fields.Float('Min. Price')
	is_buy = fields.Boolean('Is Buy', default=False)
	is_rent = fields.Boolean('Is Rent', default=False)
	max_bedroom = fields.Integer('Max Bedroom Require')
	min_bedroom = fields.Integer('Min. Bedroom Require')
	max_bathroom = fields.Integer('Max Bathroom Require')
	min_bathroom = fields.Integer('Min. Bathroom Require')
	furnished = fields.Char('Furnishing', help='Furnishing')
	type_id = fields.Many2one('property.type', 'Property Type',help='Property Type')
	email_send = fields.Boolean('Email Send', help="it is checked when email is send")

	@api.model
	def cron_property_demand(self):
		"""
		This is scheduler function which send mails to customers,
		who are demanded properties.
		@param self: The object pointer
		"""
		lead_ids = self.search([('demand','=',True)])
		property_obj = self.env['account.asset.asset']
		template_id = self.env['ir.model.data'].get_object_reference('realestate','email_template_demand_property')[1]
		if lead_ids and lead_ids.ids :
			for lead_rec in lead_ids:
				req_args = [('bedroom','<=',lead_rec.max_bedroom),
							('bedroom','>=',lead_rec.min_bedroom),
							('bathroom','<=',lead_rec.max_bathroom),
							('bathroom','>=',lead_rec.min_bathroom),
							('sale_price','<=',lead_rec.max_price),
							('sale_price','>=',lead_rec.min_price),
							('type_id','=',lead_rec.type_id.id)]
				if lead_rec.furnished == "all" and lead_rec.facing == "all":
					required_prop = property_obj.search(req_args)
				elif lead_rec.furnished == "all":
					req_args += [('facing','=',lead_rec.facing)]
					required_prop = property_obj.search(req_args)
				elif lead_rec.facing == "all":
					req_args += [('furnished','=',lead_rec.furnished)]
					required_prop = property_obj.search(req_args)
				else:
					req_args += [('furnished','=',lead_rec.furnished),('facing','=',lead_rec.facing)]
					required_prop = property_obj.search(req_args)
				if template_id and required_prop.ids and lead_rec.user_id.login and lead_rec.email_send == False:
					self.env['mail.template'].send_mail(template_id, lead_rec.id, force_send=True)
					lead_rec.write({'email_send':True})
		return True

	@api.model
	def _lead_create_contact(self, lead, name, is_company, parent_id=False):
		"""
			This method is used to create customer when lead convert to opportunity.
		@param self: The object pointer
		@param lead: The current user’s ID for security checks,
		@param name: Contact name from current Lead,
		@param is_company: Boolean field, checked if company's lead,
		@param parent_id: Linked partner from current Lead,
		@return: Newly created Partner id,
		"""
		vals = {
			'name': name,
			'user_id': lead.user_id.id,
			'comment': lead.description,
			'team_id': lead.team_id.id or False,
			'parent_id': parent_id,
			'phone': lead.phone,
			'mobile': lead.mobile,
			'email': lead.email_from,
			'fax': lead.fax,
			'title': lead.title and lead.title.id or False,
			'function': lead.function,
			'street': lead.street,
			'street2': lead.street2,
			'zip': lead.zip,
			'city': lead.city,
			'country_id': lead.country_id and lead.country_id.id or False,
			'state_id': lead.state_id and lead.state_id.id or False,
			'is_company': is_company,
			'type': 'contact',
			}
		if not lead.email_from:
			raise except_orm(_('Warning!'),_(' Contact Name or Email is Missing'))
		if lead.is_rent:
			vals.update({'tenant':True})
			tenant_id = self.env['tenant.partner'].create(vals)
			tenant_id.parent_id.write({'tenant':True})
			return tenant_id
		else:
			return self.env['res.partner'].create(vals)


class crm_make_contract(models.TransientModel):
	""" Make contract  order for crm """

	_name = "crm.make.contract"
	_description = "Make sales"

	@api.model
	def _selectPartner(self):
		"""
		This function gets default value for partner_id field.
		@param self: The object pointer
		@return: default value of partner_id field.
		"""
		if self._context is None:
			self._context = {}
		active_id = self._context and self._context.get('active_id', False) or False
		if not active_id:
			return False
		lead_brw = self.env['crm.lead'].browse(active_id)
		lead = lead_brw.read(['partner_id'])[0]
		return lead['partner_id'][0] if lead['partner_id'] else False


	date = fields.Date('End Date')
	date_start = fields.Date('Start Date',default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
	partner_id = fields.Many2one('res.partner', 'Customer',default=_selectPartner, required=True, domain=[('customer','=',True)])
	close = fields.Boolean('Mark Won',default=False, help='Check this to close the opportunity after having created the sales order.')


	@api.multi
	def makecontract(self):
		"""
		This function create Quotation on given case.
		@param self: The object pointer
		@return: Dictionary value of created sales order.
		"""
		context = dict(self._context or {})
		context.pop('default_state', False)
		data = context and context.get('active_ids', []) or []
		for make in self:
			partner = make.partner_id
			new_ids = []
			for case in self.env['crm.lead'].browse(data):
				if not partner and case.partner_id:
					partner = case.partner_id
				vals = {
					'name':case.name,
					'partner_id': partner.id,
					'company_id':partner.company_id.id,
					'date_start':make.date_start or False,
					'date':make.date or False,
					'type':'contract',
				}
				new_id = self.env['account.analytic.account'].create(vals)
				case.write({'ref': 'account.analytic.account,%s' % new_id})
				new_ids.append(new_id.id)
				message = _("Opportunity has been <b>converted</b> to the Contract <em>%s</em>.") % (new_id.name)
				case.message_post(body=message)
			if make.close:
				case.case_mark_won()
			if not new_ids:
				return {'type': 'ir.actions.act_window_close'}
			value = {
				'domain': str([('id', 'in', new_ids)]),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.analytic.account',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'name' : _('Contract'),
				'res_id': new_ids
				}

			if len(new_ids)<=1:
				value.update({'view_mode': 'form','res_id': new_ids and new_ids[0]})
			return value
