# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

class tenant_partner(models.Model):
	_name = "tenant.partner"
	_inherits = {'res.partner':'parent_id'}

	doc_name = fields.Char('Filename')
	id_attachment = fields.Binary('Identity Proof')
	tenancy_ids =fields.One2many('account.analytic.account', 'tenant_id', 'Tenancy Details', help='Tenancy Details')
	parent_id = fields.Many2one('res.partner', 'Partner', required=True, select=True, ondelete='cascade')
	tenant_ids =fields.Many2many('tenant.partner', 'agent_tenant_rel', 'agent_id', 'tenant_id', string='Tenant Details',domain=[('customer', '=',True),('agent','=',False)])
	work_address = fields.Char('Work Address')
	civil_no = fields.Char('Civil Number')

	@api.model
	def create(self, vals):
		"""
		This Method is used to overrides orm create method.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		dataobj = self.env['ir.model.data']
		property_user = False
		res = super(tenant_partner, self).create(vals)
		create_user = self.env['res.users'].create({'login': vals.get('email'),'name': vals.get('name'),
													'tenant_id': res.id,'partner_id': res.parent_id.id})
		if res.customer:
			property_user = dataobj.get_object_reference('realestate', 'group_property_user')
		if res.agent:
			property_user = dataobj.get_object_reference('realestate', 'group_property_agent')
		if property_user:
			grop_id = self.env['res.groups'].browse(property_user[1])
			grop_id.write({'users': [(4, create_user.id)]})
		return res

	@api.model
	def default_get(self, fields):
		"""
		This method is used to gets default values for tenant.
		@param self: The object pointer
		@param fields: Names of fields.
		@return: Dictionary of values.
		"""
		context = dict(self._context or {})
		res = super(tenant_partner, self).default_get(fields)
		if context.get('tenant', False):
			res.update({'tenant':context['tenant']})
		res.update({'customer':True})
		return res

	@api.multi
	def unlink(self):
		"""
		Overrides orm unlink method.
		@param self: The object pointer
		@return: True/False.
		"""
		for tenant_rec in self:
			if tenant_rec.parent_id and tenant_rec.parent_id.id:
				releted_user = tenant_rec.parent_id.id
				new_user_rec = self.env['res.users'].search([('partner_id','=',releted_user)])
				if releted_user and new_user_rec and new_user_rec.ids:
					new_user_rec.unlink()
		return super(tenant_partner, self).unlink()

class property_type(models.Model):
	_name = "property.type"

	name = fields.Char('Name', size=50, required=True)

class rent_type(models.Model):
	_name = "rent.type"
	_order='name'

	@api.multi
	@api.depends('name', 'renttype')
	def name_get(self):
		res = []
		for rec in self:
			rec_str = ''
			if rec.name:
				rec_str += rec.name
			if rec.renttype:
				rec_str += ' ' + rec.renttype + '(S)'
			res.append((rec.id, rec_str))
		return res

	@api.model
	def name_search(self,name='', args=[], operator='ilike', limit=100):
		args += ['|', ('name', operator, name), ('renttype', operator, name)]
		cuur_ids = self.search(args, limit=limit)
		return cuur_ids.name_get()

	name = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),
							 ('8','8'),('9','9'),('10','10'),('11','11'),('12','12')])
	renttype = fields.Selection([('Month','Month(S)'),('Year','Year(S)')])

class room_type(models.Model):
	_name = "room.type"

	name = fields.Char('Name', size=50, required=True)


class utility(models.Model):
	_name = "utility"

	name = fields.Char('Name', size=50, required=True)


class place_type(models.Model):
	_name = 'place.type'

	name = fields.Char('Place Type', size=50, required=True)


class maintenance_type(models.Model):
	_name = 'maintenance.type'

	name = fields.Char('Maintenance Type', size=50, required=True)

class property_phase(models.Model):
	_name = "property.phase"

	end_date = fields.Date('End Date')
	start_date = fields.Date('Beginning Date')
	commercial_tax = fields.Float('Commercial Tax (in %)')
	occupancy_rate = fields.Float('Occupancy Rate (in %)')
	lease_price = fields.Float('Sales/lease Price Per Month')
	phase_id = fields.Many2one('account.asset.asset', 'Property') 
	operational_budget = fields.Float('Operational Budget (in %)')
	company_income = fields.Float('Company Income Tax CIT (in %)')

class property_photo(models.Model):
	_name = "property.photo"

	photos = fields.Binary('Photos')
	doc_name = fields.Char('Filename')
	photos_description = fields.Char('Description')
	photo_id = fields.Many2one('account.asset.asset', 'Property')

class property_room(models.Model):
	_name = "property.room"

	note = fields.Text('Notes')
	width = fields.Float('Width')
	height = fields.Float('Height')
	length = fields.Float('Length')
	image = fields.Binary('Picture')
	name = fields.Char('Name', size=60)
	attach = fields.Boolean('Attach Bathroom')
	type_id = fields.Many2one('room.type', 'Room Type')
	assets_ids = fields.One2many('room.assets', 'room_id', 'Assets')
	property_id = fields.Many2one('account.asset.asset', 'Property')

class nearby_property(models.Model):
	_name = 'nearby.property'

	distance = fields.Float('Distance (Km)')
	name = fields.Char('Name', size=100)
	type = fields.Many2one('place.type','Type')
	property_id = fields.Many2one('account.asset.asset','Property')

class property_maintenace(models.Model):
	_name = "property.maintenance"
	_inherit = ['mail.thread']

	@api.onchange('item_ids')
	def _get_items_cost(self):
		cost = 0.0
		if self.item_ids:
			for item in self.item_ids:
				cost += (item.cost * item.quantity)
		self.items_cost = cost

	@api.onchange('items_cost', 'cost')
	def _get_total_cost(self):
		self.total_cost = self.cost + self.items_cost

	@api.onchange('property_id')
	def _get_analytic_account(self):
		if self.property_id.analytic_acc_id:
			print "               "
			print "               "
			print "               "
			print "               "
			print "               "
			print self.property_id.analytic_acc_id
			print "               "
			print "               "
			print "               "
			print "               "
			print "               "
			self.analytic_account_id = self.property_id.analytic_acc_id.id
	
	date = fields.Date('Date', default=fields.Date.context_today)
	cost = fields.Float('Cost')
	type = fields.Many2one('maintenance.type', 'Type')
	assign_to = fields.Many2one('res.partner','Assign To')
	vendor_id = fields.Many2one('res.partner','Vendor',domain=[('supplier','=',True)])
	invc_id = fields.Many2one('account.invoice','Invoice')
	vendor_invc_id = fields.Many2one('account.invoice',string='Vendor Invoice')
	renters_fault = fields.Boolean('Renters Fault', default=True,copy=True)
	invc_check = fields.Boolean('Already Created', default=False)
	vendor_invc_check = fields.Boolean('Vendor Invoice Already Created', default=False)
	mail_check = fields.Boolean('Mail Send', default=False)
	property_id = fields.Many2one('account.asset.asset','Property')
	### account_code = fields.Many2one('account.account','Receivable Account Code')
	### pay_account_code = fields.Many2one('account.account','Payable Account Code')
	notes = fields.Text('Description', size=100)
	name = fields.Selection([('Renew','Renew'),('Repair','Repair')],string="Action",default='Repair')
	state = fields.Selection([('draft', 'Draft'), ('progress', 'In Progress'), ('incomplete', 'Incomplete'), ('done', 'Done')],
							'State',default='draft')
	item_ids = fields.One2many('maintenance.item', 'maintenance_id', string='Items')
	items_cost = fields.Float('Items Cost')
	total_cost = fields.Float('Total Cost')
	analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", domain=[('is_property', '=', '')])
	

	@api.multi
	def start_maint(self):
		"""
		This Method is used to change maintenance state to progress.
		@param self: The object pointer
		"""
		return self.write({'state': 'progress'})

	@api.multi
	def cancel_maint(self):
		"""
		This Method is used to change maintenance state to incomplete.
		@param self: The object pointer
		"""
		return self.write({'state': 'incomplete'})

	@api.multi
	def send_maint_mail(self):
		"""
		This Method is used to send an email to assigned person.
		@param self: The object pointer
		"""
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('realestate','mail_template_property_maintainance')[1]
		except ValueError:
			template_id = False
		for maint_rec in self:
			if not maint_rec.assign_to.email:
				raise osv.except_osv(("Cannot send email: Assigned user has no email address."), maint_rec.assign_to.name)
			self.env['mail.template'].browse(template_id).send_mail(maint_rec.id, force_send=True, raise_exception=True)
		return self.write({'mail_check': True})

	@api.multi
	def create_invoice(self):
		"""
		This Method is used to create invoice from maintenance record.
		@param self: The object pointer
		"""
		for data in self:
			if not data.property_id.income_acc_id:
				raise Warning(_("Please Select Income Account of Property"))
			### if not data.account_code:
			### 	raise Warning(_("Please Select Receivable Account Code"))
			if not data.property_id.id:
				raise Warning(_("Please Select Property"))
			tncy_ids = self.env['account.analytic.account'].search([('property_id','=',data.property_id.id),('state','!=','close')])
			if len(tncy_ids.ids) == 0:
				raise Warning(_("No current tenancy for this property"))
			else:
				for tenancy_data in tncy_ids:
					inv_line_values = []
					maintenance_value = {
							'name': 'Maintenance For ' + data.type.name or "",
							'origin': 'property.maintenance',
							'quantity': 1,
							'account_id' : data.property_id.income_acc_id.id or False,
							'price_unit': data.cost or 0.00,
							'account_analytic_id': data.analytic_account_id.id or False,
							}
					inv_line_values.append(maintenance_value)
					
					for item in data.item_ids:
						item_value = {
							'name': item.name or "",
							'origin': 'property.maintenance',
							'quantity': item.quantity,
							'account_id' : data.property_id.income_acc_id.id or False,
							'price_unit': item.cost or 0.00,
							'account_analytic_id': data.analytic_account_id.id or False,
						}
						inv_line_values.append(item_value)

					invoice_line_ids = []
					for value in inv_line_values:
						line_id = (0, 0, value)
						invoice_line_ids.append(line_id)

					inv_type = self._context.get('type', 'out_invoice')
					inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
					company_id = self._context.get('company_id', self.env.user.company_id.id)
					domain = [
						('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
						('company_id', '=', company_id),
					]
					journal_id =  self.env['account.journal'].search(domain, limit=1)
					inv_values = {
							'origin':'Maintenance For ' + data.type.name or "",
							'type': 'out_invoice',
							'property_id':data.property_id.id,
							'partner_id' : tenancy_data.tenant_id.parent_id.id or False,
							'account_id' : tenancy_data.tenant_id.parent_id.property_account_receivable_id.id or False,
							'invoice_line_ids': invoice_line_ids,
							'amount_total' : data.cost or 0.0,
							'date_invoice' : datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT) or False,
							'number': tenancy_data.name or '',
						    'journal_id':journal_id.id,
							}
					acc_id= self.env['account.invoice'].create(inv_values)
					data.write({'renters_fault':False,'invc_check':True,'invc_id':acc_id.id,'state':'done'})
		return True

	@api.multi
	def create_vendor_invoice(self):
		"""
		This Method is used to create invoice from maintenance record.
		@param self: The object pointer
		"""
		for data in self:
			if not data.property_id.expense_acc_id:
				raise Warning(_("Please Select Expenses Account of Property"))
			# if not data.pay_account_code:
			# 	raise Warning(_("Please Select Payable Account Code"))
			if not data.property_id.id:
				raise Warning(_("Please Select Property"))
			# tncy_ids = self.env['account.analytic.account'].search([('property_id','=',data.property_id.id),('state','!=','close')])
			if not data.vendor_id:
				raise Warning(_("Please Select Vendor"))
			else:
				# for tenancy_data in tncy_ids:
				inv_line_values = []
				maintenance_value = {
						'name': 'Maintenance For ' + data.type.name or "",
						'origin': 'property.maintenance',
						'quantity': 1,
						'account_id' : data.property_id.expense_acc_id.id or False,
						'price_unit': data.cost or 0.00,
						'account_analytic_id': data.analytic_account_id.id or False,
						}
				inv_line_values.append(maintenance_value)
				
				for item in data.item_ids:
					item_value = {
						'name': item.name or "",
						'origin': 'property.maintenance',
						'quantity': item.quantity,
						'account_id' : data.property_id.expense_acc_id.id or False,
						'price_unit': item.cost or 0.00,
						'account_analytic_id': data.analytic_account_id.id or False,
					}
					inv_line_values.append(item_value)

				invoice_line_ids = []
				for value in inv_line_values:
					line_id = (0, 0, value)
					invoice_line_ids.append(line_id)

				inv_type = self._context.get('type', 'in_invoice')
				inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
				company_id = self._context.get('company_id', self.env.user.company_id.id)
				domain = [
					('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
					('company_id', '=', company_id),
				]
				journal_id =  self.env['account.journal'].search(domain, limit=1)
				inv_values = {
						'origin':'Maintenance For ' + data.type.name or "",
						'type': 'in_invoice',
						'property_id':data.property_id.id,
						'partner_id' : data.vendor_id.id or False,
						'account_id' : data.vendor_id.property_account_payable_id.id or False,
						'invoice_line_ids': invoice_line_ids,
						'amount_total' : data.cost or 0.0,
						'date_invoice' : datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT) or False,
						'number': data.property_id.name or '',
						'journal_id':journal_id.id,
						}
				acc_id= self.env['account.invoice'].create(inv_values)
				data.write({'vendor_invc_check':True,'vendor_invc_id':acc_id.id,'state':'incomplete'})
		return True

	@api.multi
	def open_invoice(self):
		"""
		This Method is used to Open invoice from maintenance record.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		wiz_form_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')[1]
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'form',
			'res_model': 'account.invoice',
			'res_id':self.invc_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}

	@api.multi
	def open_vendor_invoice(self):
		"""
		This Method is used to Open invoice from maintenance record.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		wiz_form_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_supplier_form')[1]
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'form',
			'res_model': 'account.invoice',
			'res_id':self.vendor_invc_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}

class cost_cost(models.Model):
	_name = "cost.cost"
	_order = 'date'

	@api.one
	@api.depends('move_id')
	def _get_move_check(self):
		self.move_check = bool(self.move_id)

	date = fields.Date('Date')
	amount = fields.Float('Amount')
	name = fields.Char('Description', size=100)
	payment_details = fields.Char('Payment Details',size=100)
	currency_id = fields.Many2one('res.currency', 'Currency')
	move_id = fields.Many2one('account.move', 'Purchase Entry')
	purchase_property_id = fields.Many2one('account.asset.asset', 'Property')
	remaining_amount = fields.Float('Remaining Amount', help='Shows remaining amount in currency')
	move_check = fields.Boolean(compute='_get_move_check', method=True, string='Posted', store=True)
	rmn_amnt_per = fields.Float('Remaining Amount In %', help='Shows remaining amount in Percentage')


	@api.multi
	def create_move(self):
		"""
		This button Method is used to create account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'purchase')])
		for line in self:
			depreciation_date = datetime.now()
			company_currency = line.purchase_property_id.company_id.currency_id.id
			current_currency = line.purchase_property_id.currency_id.id
			sign = -1
			move_vals = {
				'name': line.purchase_property_id.code or False,
				'date': depreciation_date,
				'journal_id': journal_ids and journal_ids.ids[0],
				'asset_id':line.purchase_property_id.id or False,
				'source':line.purchase_property_id.name or False,
				}
			move_id = self.env['account.move'].create(move_vals)
			if not line.purchase_property_id.partner_id:
				raise Warning(_('Please Select Partner From General Tab'))
			move_line_obj.create({
						    'name': line.purchase_property_id.name,
						    'ref': line.purchase_property_id.code,
						    'move_id': move_id.id,
						    'account_id': line.purchase_property_id.partner_id.property_account_payable_id.id or False,
						    'debit': 0.0,
						    'credit': line.amount,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.purchase_property_id.partner_id.id or False,
						    'currency_id': company_currency != current_currency and current_currency or False,
						    'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
						    'date': depreciation_date,
						    })
			move_line_obj.create({
						    'name': line.purchase_property_id.name,
						    'ref': line.purchase_property_id.code,
						    'move_id': move_id.id,
						    'account_id': line.purchase_property_id.category_id.account_asset_id.id,
						    'credit': 0.0,
						    'debit': line.amount,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.purchase_property_id.partner_id.id or False,
						    'currency_id': company_currency != current_currency and current_currency,
						    'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
						    'analytic_account_id': line.purchase_property_id.analytic_acc_id.id or False,
						    'date': depreciation_date,
						    'asset_id': line.purchase_property_id.id or False,
						    })
			line.write({'move_id': move_id.id})
			created_move_ids.append(move_id.id)
			move_id.write({'state':'posted','ref': 'Purchase Installment'})
		return created_move_ids
class room_assets(models.Model):
	_name = "room.assets"

	date = fields.Date('Date')
	name = fields.Char('Description', size=60)
	type = fields.Selection([('fixed', 'Fixed Assets'),('movable', 'Movable Assets'),('other', 'Other Assets')], 'Type')
	qty = fields.Float('Quantity')
	room_id = fields.Many2one('property.room', 'Property')


class property_insurance(models.Model):
	_name = "property.insurance"

	premium = fields.Float('Premium')
	end_date = fields.Date('End Date')
	doc_name  = fields.Char('Filename')
	contract = fields.Binary('Contract')
	start_date = fields.Date('Start Date')
	name = fields.Char('Description', size=60)
	policy_no = fields.Char('Policy Number', size=60)
	contact = fields.Many2one('res.company', 'Insurance Comapny')
	company_id = fields.Many2one('res.company', 'Related Company')
	property_insurance_id = fields.Many2one('account.asset.asset', 'Property')
	payment_mode_type= fields.Selection([('monthly', 'Monthly'), ('semi_annually', 'Semi Annually'),('yearly', 'Annually')], 'Payment Term', size=40)

class tenancy_rent_schedule(models.Model):
	_name = "tenancy.rent.schedule"
	#_rec_name = "tenancy_id"
	_order = 'start_date'

	@api.one
	@api.depends('move_id')
	def _get_move_check(self):
		self.move_check = bool(self.move_id)

	@api.one
	@api.depends('paid_id')
	def _get_paid_check(self):
		self.paid_check = bool(self.paid_id)

	@api.one
	@api.depends('discount_move_id')
	def _get_discount_check(self):
		self.discount_check = bool(self.discount_move_id)

	@api.one
	@api.depends('commession_move_id')
	def _get_commession_check(self):
		self.commession_check = bool(self.commession_move_id)



	note = fields.Text('Notes', help='Additional Notes.')
	currency_id = fields.Many2one('res.currency', string='Currency', required=True)
	amount = fields.Monetary(default=0.0, string='Amount', currency_field='currency_id', help="Rent Amount.")
	start_date = fields.Date('Date', help='Start Date.')
	end_date = fields.Date('End Date', help='End Date.')
	cheque_detail = fields.Char('Cheque Detail', size=30)
	move_check = fields.Boolean(compute='_get_move_check', method=True, string='Posted', store=True)
	paid_check = fields.Boolean(compute='_get_paid_check', method=True, string='Paid', store=True)
	commession_check = fields.Boolean(compute='_get_commession_check', method=True, string='Commession', store=True)
	rel_tenant_id = fields.Many2one('tenant.partner', string="Tenant")
###	rel_tenant_id = fields.Many2one('tenant.partner', string="Tenant", ondelete='restrict',related='tenancy_id.tenant_id', store=True)
	move_id = fields.Many2one('account.move', 'Depreciation Entry')
	commession_move_id = fields.Many2one('account.move', 'Commession Entry')
	paid_id = fields.Many2one('account.payment', 'Payment Record')
	property_id = fields.Many2one('account.asset.asset', 'Property', help='Property Name.')
	tenancy_id = fields.Many2one('account.analytic.account', 'Tenancy', help='Tenancy Name.')
	commession_value = fields.Float('Commession Value in Percent')
	discount_type = fields.Selection([('percent', 'Percentage'), ('fixed', 'Fixed Amount')], string="Discount Type")
	discount = fields.Float('Discount For New Accrual Move')
	discount_move_id = fields.Many2one('account.move', 'Move Entry After Discount')
	discount_check = fields.Boolean(compute='_get_discount_check', method=True, string='Discounted', store=True)

	@api.multi
	def create_move(self):
		"""
		This button Method is used to create account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])
		for line in self:
			depreciation_date = datetime.now()
			company_currency = line.tenancy_id.company_id.currency_id.id
			current_currency = line.tenancy_id.currency_id.id
			sign = -1
			move_vals = {
					'name':line.tenancy_id.name or False,
					'date': depreciation_date,
					'schedule_date':line.start_date,
					'journal_id': journal_ids and journal_ids.ids[0],
					'asset_id': line.tenancy_id.property_id.id or False,
					'source':line.tenancy_id.name or False,
					}
			move_id = self.env['account.move'].create(move_vals)
			if not line.tenancy_id.property_id.income_acc_id.id:
				raise Warning(_('Please Configure Income Account from Property'))
			move_line_obj.create({
						    'name': line.tenancy_id.name,
						    'ref': line.tenancy_id.ref,
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.property_id.income_acc_id.id or False,
						    'debit': 0.0,
						    'credit': line.tenancy_id.rent,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency or False,
						    'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
						    'date': depreciation_date,
						    })
			move_line_obj.create({
						    'name': line.tenancy_id.name,
						    'ref': 'Tenancy Rent',
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.tenant_id.parent_id.property_account_receivable_id.id,
						    'credit': 0.0,
						    'debit': line.tenancy_id.rent,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency,
						    'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
						    'analytic_account_id': line.tenancy_id.property_id.analytic_acc_id.id or False,
						    'date': depreciation_date,
						    'asset_id': line.tenancy_id.property_id.id or False,
						    })
			line.write({'move_id': move_id.id})
			created_move_ids.append(move_id.id)
			move_id.write({'ref': 'Tenancy Rent','state':'posted'})
		return created_move_ids

	@api.multi
	def open_account_move(self):
		"""
		This button Method is used to open related account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		open_move_id = self.env['ir.model.data'].get_object_reference('account', 'view_move_form')[1]
		return {
			'view_type': 'form',
			'view_id': open_move_id,
			'view_mode': 'form',
			'res_model': 'account.move',
			'res_id':self.move_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}

	@api.multi
	def create_disount_move(self):
		"""
		This button Method is used to create account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])
		for line in self:
			depreciation_date = datetime.now()
			company_currency = line.tenancy_id.company_id.currency_id.id
			current_currency = line.tenancy_id.currency_id.id
			sign = -1
			move_vals = {
					'name':line.tenancy_id.name or False,
					'date': depreciation_date,
					'schedule_date':line.start_date,
					'journal_id': journal_ids and journal_ids.ids[0],
					'asset_id': line.tenancy_id.property_id.id or False,
					'source':line.tenancy_id.name or False,
					}
			move_id = self.env['account.move'].create(move_vals)
			if not line.tenancy_id.property_id.income_acc_id.id:
				raise Warning(_('Please Configure Income Account from Property'))
			move_line_obj.create({
						    'name': line.tenancy_id.name + "Before Discount",
						    'ref': line.tenancy_id.ref or "" + "Before Discount",
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.property_id.income_acc_id.id or False,
						    'credit': 0.0,
						    'debit': line.tenancy_id.rent,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency or False,
						    'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
						    'date': depreciation_date,
						    })
			move_line_obj.create({
						    'name': line.tenancy_id.name+"Before Discount",
						    'ref': 'Tenancy Rent Before Discount',
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.tenant_id.parent_id.property_account_receivable_id.id,
						    'debit': 0.0,
						    'credit': line.tenancy_id.rent,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency,
						    'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
						    'analytic_account_id': line.tenancy_id.property_id.analytic_acc_id.id or False,
						    'date': depreciation_date,
						    'asset_id': line.tenancy_id.property_id.id or False,
						    })
			move_line_obj.create({
						    'name': line.tenancy_id.name + "After Discount",
						    'ref': line.tenancy_id.ref or "" +"After Discount",
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.property_id.income_acc_id.id or False,
						    'debit': 0.0,
						    'credit': line.tenancy_id.rent,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency or False,
						    'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
						    'date': depreciation_date,
						    })
			
			if line.discount_type == 'percent':
				act_discount = line.tenancy_id.rent*line.discount/100
			else:
				act_discount = line.discount

			move_line_obj.create({
						    'name': line.tenancy_id.name+"After Discount",
						    'ref': 'Tenancy Rent After Discount',
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.tenant_id.parent_id.property_account_receivable_id.id,
						    'credit': 0.0,
						    'debit': line.tenancy_id.rent-act_discount,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency,
						    'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
						    'analytic_account_id': line.tenancy_id.property_id.analytic_acc_id.id or False,
						    'date': depreciation_date,
						    'asset_id': line.tenancy_id.property_id.id or False,
						    })
			move_line_obj.create({
						    'name': line.tenancy_id.name+" Discount",
						    'ref': 'Discount',
						    'move_id': move_id.id,
						    'account_id': line.tenancy_id.property_id.discount_acc_id.id,
						    'credit': 0.0,
						    'debit': act_discount,
						    'journal_id': journal_ids and journal_ids.ids[0],
						    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
						    'currency_id': company_currency != current_currency and  current_currency,
						    'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
						    'analytic_account_id': line.tenancy_id.property_id.analytic_acc_id.id or False,
						    'date': depreciation_date,
						    'asset_id': line.tenancy_id.property_id.id or False,
						    })

			line.write({'discount_move_id': move_id.id})
			created_move_ids.append(move_id.id)
			move_id.write({'ref': 'Tenancy Rent After Discount','state':'posted'})
		return created_move_ids

	@api.multi
	def open_disount_move(self):
		"""
		This button Method is used to open related account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		open_move_id = self.env['ir.model.data'].get_object_reference('account', 'view_move_form')[1]
		return {
			'view_type': 'form',
			'view_id': open_move_id,
			'view_mode': 'form',
			'res_model': 'account.move',
			'res_id':self.discount_move_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}

	@api.multi
	def button_receive_rent(self):
		"""
		This button method is used to open the related
		account payment form view.
		@param self: The object pointer
		@return: Dictionary of values.
		"""

		amount= 0
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
		payment_methods = journal_ids[0].inbound_payment_method_ids or journal_ids[0].outbound_payment_method_ids
		payment_method_id = payment_methods and payment_methods[0] or False
		for tenancy_rec in self:
			amount = tenancy_rec.tenancy_id.rent
			if tenancy_rec.discount_move_id:
				amount = tenancy_rec.tenancy_id.rent - tenancy_rec.tenancy_id.rent*tenancy_rec.discount/100
			move_vals = {
						'partner_id': tenancy_rec.tenancy_id.tenant_id.parent_id.id,
						'payment_method_id':payment_method_id.id,
						'partner_type': 'customer',
						'journal_id' : journal_ids[0].id,
						'payment_type' : 'inbound',
						'communication':'Rent Received',
						'tenancy_id' : tenancy_rec.tenancy_id.id,
						'amount' : amount,
						'property_id' : tenancy_rec.tenancy_id.property_id.id,
						}
			paid_id = self.env['account.payment'].create(move_vals)
			tenancy_rec.write({'paid_id': paid_id.id})
			created_move_ids.append(paid_id.id)
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids2 = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])
		### for line in self:
		### 	depreciation_date = datetime.now()
		### 	company_currency = line.tenancy_id.company_id.currency_id.id
		### 	current_currency = line.tenancy_id.currency_id.id
		### 	sign = -1
		### 	move_vals = {
		### 			'name':line.tenancy_id.ref or False,
		### 			'date': depreciation_date,
		### 			'schedule_date':line.start_date,
		### 			'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
		### 			'asset_id': line.tenancy_id.property_id.id or False,
		### 			'source':line.tenancy_id.name or False,
		### 			}
		### 	commession_move_id = self.env['account.move'].create(move_vals)
		### 	if not line.tenancy_id.property_id.property_commession.journal_id.id:
		### 		raise Warning(_('Please Configure Commession Account from Property'))
		### 	move_line_obj.create({
		### 				    'name': line.tenancy_id.name,
		### 				    'move_id': commession_move_id.id,
		### 				    'account_id': line.tenancy_id.property_id.property_commession.journal_id.default_credit_account_id.id or False,
		### 				    'debit': 0.0,
		### 				    'credit': line.tenancy_id.rent * line.tenancy_id.property_id.property_commession.value/100,
		### 				    'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
		### 				    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
		### 				    'currency_id': company_currency != current_currency and  current_currency or False,
		### 				    'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
		### 				    'date': depreciation_date,
		### 				    })
		### 	move_line_obj.create({
		### 				    'name': line.tenancy_id.name,
		### 				    'ref': 'Tenancy Rent',
		### 				    'move_id': commession_move_id.id,
		### 				    'account_id': line.tenancy_id.property_id.property_commession.journal_id.default_debit_account_id.id,
		### 				    'credit': 0.0,
		### 				    'debit': line.tenancy_id.rent * line.tenancy_id.property_id.property_commession.value/100,
		### 				    'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
		### 				    'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
		### 				    'currency_id': company_currency != current_currency and  current_currency,
		### 				    'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
		### 				    'analytic_account_id': line.tenancy_id.id,
		### 				    'date': depreciation_date,
		### 				    'asset_id': line.tenancy_id.property_id.id or False,
		### 				    })
		### 	line.write({'commession_move_id': commession_move_id.id})
		### 	created_move_ids2.append(commession_move_id.id)
		### 	commession_move_id.write({'ref': 'Tenancy Rent Commession','state':'posted'})
		acc_pay_form_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')[1]
		return {
			'view_type': 'form',
			'view_id': acc_pay_form_id,
			'view_mode': 'form',
			'res_model': 'account.payment',
			'res_id':self.paid_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}

	@api.multi
	def open_account_paid_move(self):
		"""
		This button Method is used to open related account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		# payment_ids = self.env['account.payment'].search([('id', '=', self.paid_id.id)])
		acc_pay_form_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')[1]
		return {
			'view_type': 'form',
			'view_id': acc_pay_form_id,
			'view_mode': 'form',
			'res_model': 'account.payment',
			'res_id':self.paid_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}


	@api.multi
	def create_commession_move(self):
		"""
		This button Method is used to create account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])

		for line in self:
			amount = line.tenancy_id.rent * line.commession_value/100
			if line.discount_move_id:
				amount = line.tenancy_id.rent - line.tenancy_id.rent*line.discount/100
			if not line.commession_move_id:
				depreciation_date = datetime.now()
				company_currency = line.tenancy_id.company_id.currency_id.id
				current_currency = line.tenancy_id.currency_id.id
				sign = -1
				move_vals = {
						'name':line.tenancy_id.ref or line.tenancy_id.name or " ",
						'date': depreciation_date,
						'schedule_date':line.start_date,
						'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
						'asset_id': line.tenancy_id.property_id.id or False,
						'source':line.tenancy_id.name or False,
						}
						
				commession_move_id = self.env['account.move'].create(move_vals)
				if not line.tenancy_id.property_id.property_commession.journal_id.id:
					raise Warning(_('Please Configure Commession Account from Property'))
				# if not line.tenancy_id.property_id.property_commession.management_journal_id.id:
				# 	raise Warning(_('Please Configure Management Commession Account from Property'))
				move_line_obj.create({
								'name': line.tenancy_id.name,
								'ref': line.tenancy_id.ref,
								'move_id': commession_move_id.id,
								'account_id': line.tenancy_id.property_id.property_commession.journal_id.default_credit_account_id.id or False,
								'debit': 0.0,
								'credit': amount * line.commession_value/100,
								'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
								'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
								'currency_id': company_currency != current_currency and  current_currency or False,
								'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
								'date': depreciation_date,
								})
				move_line_obj.create({
								'name': line.tenancy_id.name,
								'ref': 'Tenancy Rent',
								'move_id': commession_move_id.id,
								'account_id': line.tenancy_id.property_id.property_commession.journal_id.default_debit_account_id.id,
								'credit': 0.0,
								'debit': amount * line.commession_value/100,
								'journal_id': line.tenancy_id.property_id.property_commession.journal_id.id,
								'partner_id': line.tenancy_id.tenant_id.parent_id.id or False,
								'currency_id': company_currency != current_currency and  current_currency,
								'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
								'analytic_account_id': line.tenancy_id.id,
								'date': depreciation_date,
								'asset_id': line.tenancy_id.property_id.id or False,
								})
				line.write({'commession_move_id': commession_move_id.id})
				created_move_ids.append(commession_move_id.id)
				commession_move_id.write({'ref': 'Tenancy Rent Commession','state':'posted'})
		return created_move_ids

	@api.multi
	def open_commession_move(self):
		"""
		This button Method is used to open related account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		open_move_id = self.env['ir.model.data'].get_object_reference('account', 'view_move_form')[1]
		return {
			'view_type': 'form',
			'view_id': open_move_id,
			'view_mode': 'form',
			'res_model': 'account.move',
			'res_id':self.commession_move_id.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context': context,
			}


class property_utility(models.Model):
	_name = "property.utility"

	note = fields.Text('Remarks')
	ref = fields.Char('Reference', size=60)
	expiry_date = fields.Date('Expiry Date')
	issue_date = fields.Date('Issuance Date')
	utility_id = fields.Many2one('utility', 'Utility')
	property_id = fields.Many2one('account.asset.asset', 'Property')
	tenancy_id = fields.Many2one('account.analytic.account', 'Tenancy')
	contact_id = fields.Many2one('tenant.partner', 'Contact', domain="[('tenant', '=', True)]")


class property_safety_certificate(models.Model):
	_name = "property.safety.certificate"

	ew = fields.Boolean('EW')
	weeks = fields.Integer('Weeks')
	ref = fields.Char('Reference', size=60)
	expiry_date = fields.Date('Expiry Date')
	name = fields.Char('Certificate', size=60, required=True)
	property_id = fields.Many2one('account.asset.asset', 'Property')
	contact_id = fields.Many2one('tenant.partner', 'Contact', domain="[('tenant', '=', True)]")


class property_attachment(models.Model):
	_name = 'property.attachment'

	doc_name = fields.Char('Filename')
	expiry_date = fields.Date('Expiry Date')
	contract_attachment = fields.Binary('Attachment')
	name = fields.Char('Description', size=64, requiered=True)
	property_id = fields.Many2one('account.asset.asset', 'Property')


class sale_cost(models.Model):
	_name = "sale.cost"
	_order = 'date'

	@api.one
	@api.depends('move_id')
	def _get_move_check(self):
		self.move_check = bool(self.move_id)

	date = fields.Date('Date')
	amount = fields.Float('Amount')
	name = fields.Char('Description', size=100)
	payment_details = fields.Char('Payment Details',size=100)
	currency_id = fields.Many2one('res.currency', 'Currency')
	move_id = fields.Many2one('account.move', 'Purchase Entry')
	sale_property_id = fields.Many2one('account.asset.asset', 'Property')
	remaining_amount = fields.Float('Remaining Amount', help='Shows remaining amount in currency')
	move_check = fields.Boolean(compute='_get_move_check', method=True, string='Posted', store=True)
	rmn_amnt_per = fields.Float('Remaining Amount In %', help='Shows remaining amount in Percentage')


	@api.multi
	def create_move(self):
		"""
		This button Method is used to create account move.
		@param self: The object pointer
		"""
		context = dict(self._context or {})
		move_line_obj = self.env['account.move.line']
		created_move_ids = []
		journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])
		for line in self:
			depreciation_date = datetime.now()
			company_currency = line.sale_property_id.company_id.currency_id.id
			current_currency = line.sale_property_id.currency_id.id
			sign = -1
			move_vals = {
					'name': line.sale_property_id.code or False,
					'date': depreciation_date,
					'journal_id': journal_ids and journal_ids.ids[0],
					'asset_id': line.sale_property_id.id or False,
					'source':line.sale_property_id.name or False,
					}
			move_id = self.env['account.move'].create(move_vals)
			if not line.sale_property_id.customer_id:
				raise Warning(_('Please Select Customer'))
			if not line.sale_property_id.income_acc_id:
				raise Warning(_('Please Select Income Account'))
			move_line_obj.create({
							'name': line.sale_property_id.name,
							'ref': line.sale_property_id.code,
							'move_id': move_id.id,
							'account_id': line.sale_property_id.income_acc_id.id or False,
							'debit': 0.0,
							'credit': line.amount,
							'journal_id': journal_ids and journal_ids.ids[0],
							'partner_id': line.sale_property_id.customer_id.id or False,
							'currency_id': company_currency != current_currency and  current_currency or False,
							'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
							'date': depreciation_date,
							})
			move_line_obj.create({
							'name': line.sale_property_id.name,
							'ref': line.sale_property_id.code,
							'move_id': move_id.id,
							'account_id': line.sale_property_id.customer_id.property_account_receivable_id.id or False,
							'credit': 0.0,
							'debit': line.amount,
							'journal_id': journal_ids and journal_ids.ids[0],
							'partner_id': line.sale_property_id.customer_id.id or False,
							'currency_id': company_currency != current_currency and  current_currency,
							'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
							'analytic_account_id': line.sale_property_id.analytic_acc_id.id or False,
							'date': depreciation_date,
							'asset_id': line.sale_property_id.id or False,
							})
			line.write({'move_id': move_id.id})
			created_move_ids.append(move_id.id)
			move_id.write({'state':'posted','ref': 'Sale Installment'})
		return created_move_ids
