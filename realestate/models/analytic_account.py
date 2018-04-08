# -*- coding: utf-8 -*-
import time 
from datetime import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class account_analytic_account(models.Model):
	_inherit = "account.analytic.account"
	_order='ref'

	@api.multi
	@api.depends('account_move_line_ids')
	def _total_deb_cre_amt_calc(self):
		"""
		This method is used to calculate Total income amount.
		@param self: The object pointer
		"""
		total = 0.0
		for tenancy_brw in self:
			total = tenancy_brw.total_debit_amt - tenancy_brw.total_credit_amt
			tenancy_brw.total_deb_cre_amt = total

	@api.multi
	@api.depends('account_move_line_ids')
	def _total_credit_amt_calc(self):
		"""
		This method is used to calculate Total credit amount.
		@param self: The object pointer
		"""
		total = 0.0
		for tenancy_brw in self:
			if tenancy_brw.account_move_line_ids and tenancy_brw.account_move_line_ids.ids:
				for debit_amt in tenancy_brw.account_move_line_ids:
					total += debit_amt.credit
			tenancy_brw.total_credit_amt = total

	@api.multi
	@api.depends('account_move_line_ids')
	def _total_debit_amt_calc(self):
		"""
		This method is used to calculate Total debit amount.
		@param self: The object pointer
		"""
		total = 0.0
		for tenancy_brw in self:
			if tenancy_brw.account_move_line_ids and tenancy_brw.account_move_line_ids.ids:
				for debit_amt in tenancy_brw.account_move_line_ids:
					total += debit_amt.debit
			tenancy_brw.total_debit_amt = total

	@api.one
	@api.depends('rent_schedule_ids','rent_schedule_ids.amount')
	def _total_amount_rent(self):
		"""
		This method is used to calculate Total Rent of current Tenancy.
		@param self: The object pointer
		@return: Calculated Total Rent.
		"""
		tot = 0.00
		if self.rent_schedule_ids and self.rent_schedule_ids.ids:
			for propety_brw in self.rent_schedule_ids:
					tot += propety_brw.amount
		self.total_rent = tot

	@api.multi
	@api.depends('deposit_return','deposit_received')
	def _get_deposit(self):
		"""
		This method is used to set deposit return and deposit received
		boolean field accordingly to current Tenancy.
		@param self: The object pointer
		"""
		for tennancy in self:
			payment_ids = self.env['account.payment'].search([('tenancy_id', '=', tennancy.id),('state', '=', 'posted')])
			if payment_ids and payment_ids.ids:
				for payment in payment_ids:
					if payment.payment_type == 'outbound':
						tennancy.deposit_return = True
					elif payment.payment_type == 'inbound':
						tennancy.deposit_received = True

	@api.onchange('building_id')
	def _get_floor(self):
		floor_ids = self.env['account.asset.asset'].search([('parent_id', '=', self.building_id.id), ('type_id', '=', 'floor')])	
		o_floor_ids = []
		o_flat_ids = []
		if floor_ids:
			for floor in floor_ids:
				o_floor_ids.append(floor.id)
				flat_ids = self.env['account.asset.asset'].search([('parent_id', '=', floor.id), ('type_id', 'in', ['flat', 'shop', 'office', 'basement', 'ann'])])
				if flat_ids:
					for flat in flat_ids:
						o_flat_ids.append(flat.id)
		else:
			flat_ids = self.env['account.asset.asset'].search([('parent_id', '=', self.building_id.id), ('type_id', 'in', ['flat', 'shop', 'office', 'basement', 'ann'])])
			if flat_ids:
				for flat in flat_ids:
					o_flat_ids.append(flat.id)
		floor_domain = [('id', 'in', o_floor_ids)]
		flat_domain = [('id', 'in', o_flat_ids)]
		return {
		'domain':{
			'floor_id': floor_domain,
			'property_id': flat_domain,
			}
		}

	@api.onchange('floor_id')
	def _get_flat(self):
		flat_ids = self.env['account.asset.asset'].search([('parent_id', '=', self.floor_id.id), ('type_id', 'in', ['flat', 'shop', 'office', 'basement', 'ann'])])	
		ids = []
		if flat_ids:
			for flat in flat_ids:
				ids.append(flat.id)
		flat_domain = [('id', 'in', ids)]
		return {
		'domain':{'property_id': flat_domain}
		}




	contract_attachment =  fields.Binary('Tenancy Contract')
	is_property = fields.Boolean('Is Property?')
	rent_entry_chck = fields.Boolean('Rent Entries Check', default=False)
	deposit_received =  fields.Boolean(compute='_get_deposit', method=True, default=False, multi='deposit', string='Deposit Received?', help="True if deposit amount received for current Tenancy.")
	deposit_return = fields.Boolean(compute='_get_deposit', method=True,default=False, multi='deposit', type='boolean', string='Deposit Returned?', help="True if deposit amount returned for current Tenancy.")
	ref = fields.Char('Reference')
	doc_name =  fields.Char('Filename')
	date = fields.Date('Expiration Date', select=True, help="Tenancy contract end date.")
	date_start = fields.Date('Start Date',default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), help="Tenancy contract start date .")
	ten_date = fields.Date('Date', select=True, default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), help="Tenancy contract creation date.")
	amount_fee_paid = fields.Integer('Amount of Fee Paid')
	manager_id =  fields.Many2one('res.users', 'Account Manager', help="Manager of Tenancy.") 
	tenant_id = fields.Many2one('tenant.partner', 'Tenant', domain="[('tenant', '=', True)]", help="Tenant Name of Tenancy.")
	contact_id = fields.Many2one('res.partner', 'Contact', help="Contact person name.")
	currency_id = fields.Many2one('res.currency', string='Currency',help="The optional other currency if it is a multi-currency entry.")
	rent_schedule_ids = fields.One2many('tenancy.rent.schedule', 'tenancy_id', 'Rent Schedule')
	account_move_line_ids = fields.One2many('account.move.line', 'analytic_account_id', 'Entries', readonly=True, states={'draft':[('readonly',False)]})
	rent = fields.Monetary(default=0.0, string='Tenancy Rent', currency_field='currency_id', help="Tenancy rent for selected property per Month.")
	deposit = fields.Monetary(default=0.0, string='Deposit', currency_field='currency_id', help="Deposit amount for Tenancy.")
	total_rent = fields.Monetary(compute='_total_amount_rent', string='Total Rent', readonly=True, store=True, currency_field='currency_id', help='Total rent of this Tenancy.')
	amount_return = fields.Monetary(default=0.0, string='Deposit Returned', currency_field='currency_id', help="Deposit Returned amount for Tenancy.")
	total_debit_amt = fields.Monetary(compute='_total_debit_amt_calc', string='Total Debit Amount', default=0.0, currency_field='currency_id')
	total_credit_amt = fields.Monetary(compute='_total_credit_amt_calc', string='Total Credit Amount', default=0.0, currency_field='currency_id')
	total_deb_cre_amt = fields.Monetary(compute='_total_deb_cre_amt_calc', string='Total Expenditure', default=0.0, currency_field='currency_id')
	description  = fields.Text('Description', help='Additional Terms and Conditions')
	duration_cover = fields.Text('Duration of Cover', help='Additional Notes')
	acc_pay_dep_rec_id = fields.Many2one('account.payment', 'Account Manager', help="Manager of Tenancy.")
	acc_pay_dep_ret_id = fields.Many2one('account.payment', 'Account Manager', help="Manager of Tenancy.")
	rent_type_id = fields.Many2one('rent.type', 'Rent Type')
	deposit_scheme_type = fields.Selection([('insurance', 'Insurance-based'),], 'Type of Scheme')
	state =  fields.Selection([('template', 'Template'),('draft','New'),('open','In Progress'),
								('pending','To Renew'),('close','Closed'),('cancelled', 'Cancelled')],
								'Status', required=True,copy=False, default='draft')
	sched = fields.Selection([('start_date', 'Start Date'), ('chosen_date', 'Chosen Date')], string='Schedule Start From', default='start_date')
	sched_date = fields.Date('Date')
	renter = fields.Many2one('res.partner', 'Renter')
	renter_company = fields.Many2one('res.partner', 'Renter Company', domain=[('is_company', '=', True)])
	building_id = fields.Many2one('account.asset.asset', string="Building", domain=[('type_id', '=', 'building')])
	floor_id = fields.Many2one('account.asset.asset', string="Floor")
	property_id = fields.Many2one('account.asset.asset','Flat', help="Name of Property.")

	

	@api.model
	def create(self, vals):
		"""
		This Method is used to overrides orm create method,
		to change state and tenant of related property.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		if not vals:
			vals = {}
		if vals.has_key('tenant_id'):
			vals['ref'] = self.env['ir.sequence'].next_by_code('account.analytic.account')
			vals.update({'is_property':True})
		if vals.has_key('property_id'):
			tenancy_id = self.env['account.analytic.account'].search([('property_id', '=', vals['property_id']), ('state', '=', 'open')])
			if tenancy_id:
				raise Warning(_('this property is already rented ...'))
			prop_brw = self.env['account.asset.asset'].browse(vals['property_id'])
			prop_brw.write({'current_tenant_id': vals['tenant_id'],'state': 'book'})
		return super(account_analytic_account, self).create(vals)

	@api.multi
	def write(self, vals):
		"""
		This Method is used to overrides orm write method,
		to change state and tenant of related property.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		for tenancy_rec in self:
			rec = super(account_analytic_account, self).write(vals)
			if vals.get('state'):
				if vals['state'] == 'open':
					tenancy_rec.property_id.write({'current_tenant_id': tenancy_rec.tenant_id.id,
													'state': 'normal'})
				if vals['state'] == 'close':
					tenancy_rec.property_id.write({'state': 'draft','current_tenant_id':False})
		return rec

	@api.multi
	def unlink(self):
		"""
		Overrides orm unlink method,
		@param self: The object pointer
		@return: True/False.
		"""
		rent_ids = []
		for tenancy_rec in self:
			analytic_ids = self.env['account.analytic.line'].search([('account_id','=',tenancy_rec.id)])
			if analytic_ids and analytic_ids.ids:
				analytic_ids.unlink()
			rent_ids = self.env['tenancy.rent.schedule'].search([('tenancy_id','=',tenancy_rec.id)])
			post_rent = [x.id for x in rent_ids if x.move_check == True]
			if post_rent:
				raise Warning(_('You cannot delete Tenancy record, if any related Rent Schedule entries are in posted.'))
			else:
				rent_ids.unlink()
			if tenancy_rec.property_id.property_manager and tenancy_rec.property_id.property_manager.id:
				releted_user = tenancy_rec.property_id.property_manager.id
				new_ids = self.env['res.users'].search([('partner_id','=',releted_user)])
				if releted_user and new_ids and new_ids.ids:
					new_ids.write({'tenant_ids':[(3, tenancy_rec.tenant_id.id)]})
			tenancy_rec.property_id.write({'state': 'draft','current_tenant_id':False})
		return super(account_analytic_account, self).unlink()

	@api.onchange('property_id')
	def onchange_property_id(self):
		"""
		This Method is used to set property related fields value,
		on change of property.
		@param self: The object pointer
		"""
		if self.property_id:
			self.rent = self.property_id.ground_rent or False
			self.rent_type_id = self.property_id.rent_type_id and self.property_id.rent_type_id.id or False

	@api.multi
	def button_receive(self):
		"""
		This button method is used to open the related
		account payment form view.
		@param self: The object pointer
		@return: Dictionary of values.
		"""
		if not self._ids: return []
		for tenancy_rec in self:
			if tenancy_rec.acc_pay_dep_rec_id and tenancy_rec.acc_pay_dep_rec_id.id:
				acc_pay_form_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')[1]
				return {
					'view_type': 'form',
					'view_id': acc_pay_form_id,
					'view_mode': 'form',
					'res_model': 'account.payment',
					'res_id':self.acc_pay_dep_rec_id.id,
					'type': 'ir.actions.act_window',
					'target': 'current',
					'context': self._context,
					}
			if tenancy_rec.deposit == 0.00:
				raise Warning(_('Please Enter Deposit amount.'))
			if not tenancy_rec.property_id.income_acc_id.id:
				raise Warning(_('Please Configure Income Account from Property.'))
			ir_id = self.env['ir.model.data']._get_id('account', 'view_account_payment_form')
			ir_rec = self.env['ir.model.data'].browse(ir_id)
			return {
				'view_mode': 'form',
				'view_id': [ir_rec.res_id],
				'view_type': 'form',
				'res_model': 'account.payment',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'domain': '[]',
				'context': {
					'default_partner_id': tenancy_rec.tenant_id.parent_id.id,
					'default_partner_type': 'customer',
					'default_journal_id' : 6,
					'default_payment_type' : 'inbound',
					'default_communication':'Deposit Received',
					'default_tenancy_id' : tenancy_rec.id,
					'default_amount' : tenancy_rec.deposit,
					'default_property_id' : tenancy_rec.property_id.id,
					'close_after_process': True,
					}
			}

	@api.multi
	def button_return(self):
		"""
		This button method is used to open the related
		account payment form view.
		@param self: The object pointer
		@return: Dictionary of values.
		"""
		if not self._ids: return []
		for tenancy_rec in self:
			if tenancy_rec.acc_pay_dep_ret_id and tenancy_rec.acc_pay_dep_ret_id.id:
				acc_pay_form_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')[1]
				return {
					'view_type': 'form',
					'view_id': acc_pay_form_id,
					'view_mode': 'form',
					'res_model': 'account.payment',
					'res_id':self.acc_pay_dep_ret_id.id,
					'type': 'ir.actions.act_window',
					'target': 'current',
					'context': self._context,
					}
			if tenancy_rec.amount_return == 0.00:
				raise Warning(_('Please Enter Deposit Returned amount'))
			if not tenancy_rec.property_id.income_acc_id.id:
				raise Warning(_('Please Configure Income Account from Property'))
			ir_id = self.env['ir.model.data']._get_id('account', 'view_account_payment_form')
			ir_rec = self.env['ir.model.data'].browse(ir_id)
			return {
				'view_mode': 'form',
				'view_id': [ir_rec.res_id],
				'view_type': 'form',
				'res_model': 'account.payment',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'domain': '[]',
				'context': {
					'default_partner_id': tenancy_rec.tenant_id.parent_id.id,
					'default_partner_type': 'customer',
					'default_journal_id' : 6,
					'default_payment_type' : 'outbound',
					'default_communication':'Deposit Return',
					'default_tenancy_id' : tenancy_rec.id,
					'default_amount' : tenancy_rec.amount_return,
					'default_property_id' : tenancy_rec.property_id.id,
					'close_after_process': True,
					}
			}

	@api.multi
	def button_start(self):
		"""
		This button method is used to Change Tenancy state to Open.
		@param self: The object pointer
		"""
		for current_rec in self:
			if current_rec.property_id.property_manager and current_rec.property_id.property_manager.id:
				releted_user = current_rec.property_id.property_manager.id
				new_ids = self.env['res.users'].search([('partner_id','=',releted_user)])
				if releted_user and new_ids and new_ids.ids:
					new_ids.write({'tenant_ids':[(4, current_rec.tenant_id.id)]})
		return self.write({'state':'open','rent_entry_chck':False})

	@api.multi
	def button_close(self):
		"""
		This button method is used to Change Tenancy state to close.
		@param self: The object pointer
		"""
		return self.write({'state':'close'})

	@api.multi
	def set_draft(self):
		if self.rent_schedule_ids:
			for rent in self.rent_schedule_ids:
				if rent.move_check or rent.paid_check or rent.commession_check or rent.commession_check2 or rent.discount_check:
					raise Warning(_('There is at least one generated move, payment, commisiion or discount remove it first !!'))
				else:
					rent.unlink()
				# if rent.paid_check:
				# 	raise Warning(_('There is at least one generated payment, remove it first !!'))
				# if rent.commession_check:
				# 	raise Warning(_('There is at least one generated commission, remove it first !!'))
				# if rent.commession_check2:
				# 	raise Warning(_('There is at least one generated commission, remove it first !!'))
				# if rent.discount_check:
				# 	raise Warning(_('There is at least one generated discount, remove it first !!'))
				
		return self.write({
			'state': 'draft',
			})

	@api.multi
	def button_set_to_draft(self):
		"""
		This Method is used to open Tenancy renew wizard.
		@param self: The object pointer
		@return: Dictionary of values.
		"""
		cr, uid, context = self.env.args
		context = dict(context)
		if context is None:
			context = {}
		for tenancy_brw in self:
			tenancy_rent_ids = self.env['tenancy.rent.schedule'].search([('tenancy_id', '=', tenancy_brw.id), ('move_check', '=',False)])
			if len(tenancy_rent_ids.ids) > 0:
				raise Warning(_('In order to Renew a Tenancy, Please make all related Rent Schedule entries posted.'))
			context.update({'edate': tenancy_brw.date})
			return {
				'name': ('Tenancy Renew Wizard'),
				'res_model': 'renew.tenancy',
				'type': 'ir.actions.act_window',
				'view_id': False,
				'view_mode': 'form',
				'view_type': 'form',
				'target': 'new',
				'context': {'default_start_date': context.get('edate')}
			}

	@api.model
	def cron_property_states_changed(self):
		"""
		This Method is called by Scheduler for change property state
		according to tenancy state.
		@param self: The object pointer
		"""
		curr_date = datetime.now().date()
		tncy_ids = self.search([('date_start','<=',curr_date),('date','>=',curr_date),('state','=','open'),('is_property','=',True)])
		if len(tncy_ids.ids) != 0:
			for tncy_data in tncy_ids:
				if tncy_data.property_id and tncy_data.property_id.id:
					tncy_data.property_id.write({'state':'normal','color':7})
		return True

	@api.model
	def cron_property_tenancy(self):
		"""
		This Method is called by Scheduler to send email
		to tenant as a reminder for rent payment.
		@param self: The object pointer
		"""
		tenancy_ids = []
		due_date = datetime.now().date() + relativedelta(days=7)
		tncy_ids = self.search([('is_property','=',True),('state','=','open')])
		for tncy_data in tncy_ids:
			tncy_rent_ids = self.env['tenancy.rent.schedule'].search([('tenancy_id','=',tncy_data.id),('start_date','=',due_date)])
			if tncy_rent_ids and tncy_rent_ids.ids:
				tenancy_ids.append(tncy_data.id)
		tenancy_sort_ids = list(set(tenancy_ids))
		model_data_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_email_template')[1]
		template_brw = self.env['mail.template'].browse(model_data_id)
		for tenancy in tenancy_sort_ids:
			template_brw.send_mail(tenancy, force_send=True, raise_exception=False)
		return True

	@api.multi
	def create_rent_schedule(self):
		"""
		This button method is used to create rent schedule Lines.
		@param self: The object pointer
		"""
		rent_obj = self.env['tenancy.rent.schedule']
		for tenancy_rec in self:
			if tenancy_rec.rent_type_id.renttype == 'Month':
				interval = int(tenancy_rec.rent_type_id.name)
			if tenancy_rec.rent_type_id.renttype == 'Year':
				interval = int(tenancy_rec.rent_type_id.name) * 12
			if tenancy_rec.sched == 'start_date':
				d1 = datetime.strptime(tenancy_rec.date_start, DEFAULT_SERVER_DATE_FORMAT)
			elif tenancy_rec.sched == 'chosen_date':
				d1 = datetime.strptime(tenancy_rec.sched_date, DEFAULT_SERVER_DATE_FORMAT)
			d2 = datetime.strptime(tenancy_rec.date, DEFAULT_SERVER_DATE_FORMAT)
			diff = abs((d1.year - d2.year)*12 + (d1.month - d2.month))
			tot_rec = diff / interval
			tot_rec2 = diff % interval
			if abs(d1.month - d2.month) >= 0 and d1.day < d2.day:
				tot_rec2 += 1
			if diff == 0:
				tot_rec2 = 1
			if tot_rec > 0:
				for rec in range(tot_rec):
					rent_obj.create({
							'start_date': d1.strftime(DEFAULT_SERVER_DATE_FORMAT),
							'amount':tenancy_rec.rent*interval or 0.0,
							'property_id':tenancy_rec.property_id and tenancy_rec.property_id.id or False,
							'commession_value':tenancy_rec.property_id.property_commession.value,
							'tenancy_id': tenancy_rec.id,
							'currency_id':tenancy_rec.currency_id.id or False,
							'rel_tenant_id':tenancy_rec.tenant_id.id
							})
					d1 = d1 + relativedelta(months=interval)
			if tot_rec2 > 0:
				rent_obj.create({
							'start_date': d1.strftime(DEFAULT_SERVER_DATE_FORMAT),
							'amount':tenancy_rec.rent*tot_rec2 or 0.0,
							'property_id':tenancy_rec.property_id and tenancy_rec.property_id.id or False,
							'commession_value':tenancy_rec.property_id.property_commession.value,
							'tenancy_id': tenancy_rec.id,
							'currency_id':tenancy_rec.currency_id.id or False,
							'rel_tenant_id':tenancy_rec.tenant_id.id
							})
		return self.write({'rent_entry_chck':True})

	@api.multi
	def action_get_template(self):
		action = self.env.ref('realestate_contract.tenancy_contract_action').read()[0]
		tenancy_id = self.id
		action['domain'] = [('tenancy_id.id', '=', tenancy_id)]
		return action