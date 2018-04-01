# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning, ValidationError

class crossovered_budget_lines(models.Model):

	_inherit = "crossovered.budget.lines"

	asset_id = fields.Many2one('account.asset.asset','Property')


class account_asset_asset(models.Model):
	_inherit = 'account.asset.asset'
	_description = 'Asset'


	@api.multi
	@api.depends('image')
	def _has_image(self):
		"""
			This method is used to set Property image.
		@param self: The object pointer
		@return: True or False
		"""
		result = False
		for p in self:
			if p.image:
				result = bool(p.image)
			p.has_image = result

	@api.multi
	@api.depends('date','tenancy_property_ids','tenancy_property_ids.date','tenancy_property_ids.date_start')
	def occupancy_calculation(self):
		"""
			This Method is used to calculate occupancy rate.
		@param self: The object pointer
		@return: Calculated Occupancy Rate.
		"""
		occ_rate = 0
		diffrnc = 0
		for prop_rec in self:
			prop_date = datetime.strptime(prop_rec.date, DEFAULT_SERVER_DATE_FORMAT).date()
			pur_diff = datetime.now().date() - prop_date
			purchase_diff = pur_diff.days
			if prop_rec.tenancy_property_ids and prop_rec.tenancy_property_ids.ids:
				for tency_rec in prop_rec.tenancy_property_ids:
					if tency_rec.date and tency_rec.date_start:
						date_diff = datetime.strptime(tency_rec.date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(tency_rec.date_start, DEFAULT_SERVER_DATE_FORMAT)
						diffrnc += date_diff.days
			if purchase_diff != 0 and diffrnc != 0:
				occ_rate = (purchase_diff * 100) / diffrnc
			prop_rec.occupancy_rates = occ_rate

	@api.multi
	@api.depends('property_phase_ids','property_phase_ids.lease_price')
	def sales_rate_calculation(self):
		"""
			This Method is used to calculate total sales rates.
		@param self: The object pointer
		@return: Calculated Sales Rate.
		"""
		sal_rate = 0
		counter = 0
		les_price = 0
		for prop_rec in self:
			if prop_rec.property_phase_ids and prop_rec.property_phase_ids.ids:
				for phase in prop_rec.property_phase_ids:
					counter = counter + 1
					les_price += phase.lease_price
				if counter != 0 and les_price != 0:
					sal_rate = les_price / counter
			prop_rec.sales_rates = sal_rate

	@api.multi
	@api.depends('maintenance_ids','maintenance_ids.cost','tenancy_property_ids','tenancy_property_ids.rent')
	def roi_calculation(self):
		"""
			This Method is used to Calculate ROI(Return On Investment).
		@param self: The object pointer
		@return: Calculated Return On Investment.
		"""
		cost_of_investment = 0
		gain_from_investment = 0
		total = 0
		for prop_rec in self:
			if prop_rec.maintenance_ids and prop_rec.maintenance_ids.ids:
				for maintenance in prop_rec.maintenance_ids:
					cost_of_investment += maintenance.cost
			if prop_rec.tenancy_property_ids and prop_rec.tenancy_property_ids.ids:
				for gain in prop_rec.tenancy_property_ids:
					gain_from_investment += gain.rent
			if (cost_of_investment != 0 and gain_from_investment !=0 and cost_of_investment != gain_from_investment):
				total = (gain_from_investment - cost_of_investment) / cost_of_investment
			prop_rec.roi = total

	@api.one
	@api.depends('roi')
	def ten_year_roi_calculation(self):
		"""
			This Method is used to Calculate ten years ROI(Return On Investment).
		@param self: The object pointer
		@return: Calculated Return On Investment.
		"""
		self.ten_year_roi = 10 * self.roi

	@api.one
	@api.depends('purchase_price','ground_rent')
	def calc_return_period(self):
		"""
		This Method is used to Calculate Return Period.
		@param self: The object pointer
		@return: Calculated Return Period.
		"""
		rtn_prd = 0
		if self.ground_rent != 0 and self.purchase_price != 0:
			rtn_prd = self.purchase_price / self.ground_rent
		self.return_period = rtn_prd

	@api.multi
	@api.depends('tenancy_property_ids','tenancy_property_ids.rent','property_phase_ids','property_phase_ids.operational_budget')
	def operation_cost(self):
		"""
			This Method is used to Calculate Operation Cost.
		 @param self: The object pointer
		@return: Calculated Operational Cost.
		"""
		operational_cost = 0
		opr_cst = 0
		gain_from_investment = 0
		for prop_rec in self:
			if prop_rec.tenancy_property_ids and prop_rec.tenancy_property_ids.ids:
				for gain in prop_rec.tenancy_property_ids:
					gain_from_investment += gain.rent
			if prop_rec.property_phase_ids and prop_rec.property_phase_ids.ids:
				for phase in prop_rec.property_phase_ids:
					operational_cost += ((phase.operational_budget * phase.lease_price) / 100)
			if gain_from_investment != 0 and operational_cost != 0:
				opr_cst = operational_cost / gain_from_investment
			prop_rec.operational_costs = opr_cst

	@api.multi
	@api.depends('tenancy_property_ids','tenancy_property_ids.rent_schedule_ids')
	def cal_simulation(self):
		"""
			This Method is used to calculate simulation
			which is used in Financial Performance Report.
		@param self: The object pointer
		@return: Calculated Simulation Amount.
		"""
		amt = 0.0
		for property_data in self:
			if property_data.tenancy_property_ids and property_data.tenancy_property_ids.ids:
				for tncy in property_data.tenancy_property_ids:
					if tncy.rent_schedule_ids and tncy.rent_schedule_ids.ids:
						for prty_tncy_data in tncy.rent_schedule_ids:
							amt += prty_tncy_data.amount
			property_data.simulation = amt

	@api.multi
	@api.depends('tenancy_property_ids','tenancy_property_ids.rent_schedule_ids','tenancy_property_ids.rent_schedule_ids.move_check')
	def cal_revenue(self):
		"""
			This Method is used to calculate revenue
			which is used in Financial Performance Report.
		@param self: The object pointer
		@return: Calculated Revenue Amount.
		"""
		amt = 0.0
		for property_data in self:
			if property_data.tenancy_property_ids and property_data.tenancy_property_ids.ids:
				for tncy in property_data.tenancy_property_ids:
					if tncy.rent_schedule_ids and tncy.rent_schedule_ids.ids:
						for prty_tncy_data in tncy.rent_schedule_ids:
							if prty_tncy_data.move_check == True:
								amt += prty_tncy_data.amount
			property_data.revenue = amt

	@api.one
	@api.depends('value', 'salvage_value', 'depreciation_line_ids')
	def _amount_residual(self):
		"""
		@param self: The object pointer
		@return: Calculated Residual Amount.
		"""
		total_amount = 0.0
		total_residual = 0.0
		if self.value > 0:
			for line in self.depreciation_line_ids:
				if line.move_check:
					total_amount += line.amount
			total_residual = self.value - total_amount - self.salvage_value
		self.value_residual = total_residual

	@api.one
	@api.depends('gfa_feet', 'unit_price')
	def cal_total_price(self):
		"""
			This Method is used to Calculate Total Price.
		@param self: The object pointer
		@return: Calculated Total Price.
		"""
		self.total_price = self.gfa_feet * self.unit_price


	image = fields.Binary('Image')
	note = fields.Text('Notes' , help='Additional Notes.')
	sale_date = fields.Date('Sale Date', help='Sale Date of the Property.')
	end_date = fields.Date('End Date')
	simulation_date = fields.Date('Simulation Date', help='Simulation Date.')
	age_of_property = fields.Date('Date', default=fields.Date.context_today, help='Property Creation Date.')
	city = fields.Char('City')
	street = fields.Char('Street')
	street2 = fields.Char('Street2')
	township = fields.Char('Township')
	simulation_name = fields.Char('Simulation Name')
	construction_cost = fields.Char('Construction Cost')
	zip = fields.Char('Zip', size=24, change_default=True)
	video_url = fields.Char('Video URL', help="//www.youtube.com/embed/mwuPTI8AT7M?rel=0")
	unit_price = fields.Float('Unit Price', help='Unit Price Per Sqft.')
	ground_rent = fields.Float('Ground Rent', help='Ground rent of Property.')
	gfa_meter = fields.Float('GFA(m)',help='Gross floor area in Meter.')
	sale_price = fields.Float('Sale Price', help='Sale price of the Property.')
	gfa_feet = fields.Float('GFA(Sqft)',help='Gross floor area in Square feet.')
	purchase_price = fields.Float('Purchase Price', help='Purchase price of the Property.')
	sales_rates = fields.Float(compute='sales_rate_calculation',string="Sales Rate", help='Average Sale/Lease price from property phase per Month.')
	ten_year_roi = fields.Float(compute='ten_year_roi_calculation', string="10year ROI", help="10year Return of Investment.")
	roi = fields.Float(compute='roi_calculation', string="ROI",store=True, help='ROI ( Return On Investment ) = ( Total Tenancy rent - Total maintenance cost ) / Total maintenance cost.',)
	operational_costs = fields.Float(compute='operation_cost',string="Operational Costs(%)", store=True, help='Average of total operational budget and total rent.')
	occupancy_rates = fields.Float(compute='occupancy_calculation',string="Occupancy Rate", store=True, help='Total Occupancy rate of Property.')
	value_residual = fields.Float(compute='_amount_residual', method=True, digits_compute=dp.get_precision('Account'), string='Residual Value')
	return_period = fields.Float(compute='calc_return_period',string="Return Period(In Months)", store=True, help='Average of Purchase Price and Ground Rent.')
	simulation = fields.Float(compute='cal_simulation',string='Total Amount', store=True)
	revenue = fields.Float(compute='cal_revenue',string='Revenue',store=True)
	total_price = fields.Float(compute='cal_total_price', string='Total Price', help='Total Price of Property, \nTotal Price = Unit Price * GFA (Sqft) .')
	multiple_owners = fields.Boolean('Multiple Owners', help="Check this box if there is multiple Owner of the Property.")
	has_image = fields.Boolean(compute='_has_image')
	pur_instl_chck = fields.Boolean('Purchase Installment Check', default=False)
	sale_instl_chck = fields.Boolean('Sale Installment Check', default=False)
	color = fields.Integer('Color', default=4)
	total_owners = fields.Integer('Number of Owners')
	floor = fields.Integer('Floor', help='Number of Floors.')
	no_of_towers = fields.Integer('No of Towers', help='Number of Towers.')
	no_of_property = fields.Integer('Property Per Floors.', help='Number of Properties Per Floor.')
	customer_id = fields.Many2one('res.partner', 'Customer')
	income_acc_id = fields.Many2one('account.account', 'Income Account', help='Income Account of Property.')
	expense_acc_id = fields.Many2one('account.account', 'Expenses Account', help='Expenses Account of Property.')
	parent_id = fields.Many2one('account.asset.asset', 'Parent Property')
	current_tenant_id = fields.Many2one('tenant.partner','Current Tenant')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
	#type_id = fields.Many2one('property.type', 'Property Type',help='Property Type.')
	type_id = fields.Selection([('building', 'Building'), ('floor', 'Floor'), ('flat', 'Flat')], string='Property Type')
	analytic_acc_id = fields.Many2one('account.analytic.account', 'Analytic Account')
	rent_type_id = fields.Many2one('rent.type', 'Rent Type', help='Type of Rent.')
	contact_id = fields.Many2one('tenant.partner', 'Contact Name', domain="[('tenant', '=', True)]")
	payment_term = fields.Many2one('account.payment.term', 'Payment Terms')
	property_manager = fields.Many2one('res.partner', 'Property Manager',help="Manager of Property.")
	room_ids = fields.One2many('property.room', 'property_id', 'Rooms')
	sale_cost_ids = fields.One2many('sale.cost', 'sale_property_id', 'Costs')
	property_phase_ids = fields.One2many('property.phase', 'phase_id', 'Phase')
	property_photo_ids = fields.One2many('property.photo', 'photo_id', 'Photos')
	utility_ids = fields.One2many('property.utility', 'property_id', 'Utilities')
	nearby_ids = fields.One2many('nearby.property','property_id','Nearest Property')
	purchase_cost_ids = fields.One2many('cost.cost', 'purchase_property_id', 'Costs')
	maintenance_ids = fields.One2many('property.maintenance', 'property_id', 'Maintenance')
	contract_attachment_ids = fields.One2many('property.attachment', 'property_id', 'Document')
	child_ids = fields.One2many('account.asset.asset', 'parent_id', 'Children Assets')
	property_insurance_ids = fields.One2many('property.insurance', 'property_insurance_id', 'Insurance')
	tenancy_property_ids = fields.One2many('account.analytic.account', 'property_id', 'Tenancy Property')
	#crossovered_budget_line_property_ids = fields.Many2many('crossovered.budget.lines', 'asset_id', 'Budget Lines')
	crossovered_budget_line_property_ids = fields.One2many('crossovered.budget.lines', 'asset_id', 'Budget Lines')
	safety_certificate_ids = fields.One2many('property.safety.certificate', 'property_id', 'Safety Certificate')
	#account_move_ids =  fields.Many2many('account.move', 'asset_id', 'Entries', readonly=True, states={'draft':[('readonly',False)]})
	account_move_ids =  fields.One2many('account.move', 'asset_id', 'Entries', readonly=True, states={'draft':[('readonly',False)]})
	#depreciation_line_ids = fields.Many2many('account.asset.depreciation.line', 'asset_id', 'Depreciation Lines', readonly=True, states={'draft':[('readonly', False)]})
	depreciation_line_ids = fields.One2many('account.asset.depreciation.line', 'asset_id', string='Depreciation Lines', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
	bedroom = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5+')],'Bedrooms',default='1')
	bathroom = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5+')],'Bathrooms',default='1')
	recurring_rule_type = fields.Selection([('monthly', 'Month(s)')],'Recurrency', default='monthly', help="Invoice automatically repeat at specified interval.")
	facing = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], 'Facing', default='east')
	furnished = fields.Selection([('none', 'None'),('semi_furnished', 'Semi Furnished'),
									('full_furnished', 'Full Furnished')], 'Furnishing', default='none', help='Furnishing.')
	state = fields.Selection([('new_draft', 'Booking Open'), ('draft', 'Available'), ('book', 'Booked'), ('normal', 'On Lease'), ('close', 'Sale'), ('sold', 'Sold'), ('cancel', 'Cancel')], 'State',
							required=True, default='draft')
	rent_type_id = fields.Many2one('rent.type', 'Rent Type')
	lat = fields.Float('Latitude')
	lon = fields.Float('Longitude')
	wallet_id = fields.Many2one('realestate.wallet', 'Wallet')
	is_prop = fields.Boolean('Is Property')
	property_no = fields.Integer('Property Number')
	piece_no = fields.Integer('Piece Number')

	@api.model
	def create(self, vals):
		"""
		This Method is used to overrides orm create method.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		if not vals:
			vals = {}
		if vals.has_key('message_follower_ids'):
			del vals['message_follower_ids']
		vals['code'] = self.env['ir.sequence'].next_by_code('property')
		if vals.get('parent_id'):
			parent_periods = self.browse(vals.get('parent_id'))
			if parent_periods.rent_type_id and parent_periods.rent_type_id.id:
				vals.update({'rent_type_id':parent_periods.rent_type_id.id})
		asset_id = super(account_asset_asset, self).create(vals)
		#acc_analytic_id = self.env['account.analytic.account'].create({'name':vals['name']})
		return asset_id

	@api.multi
	def write(self, vals):
		"""
		This Method is used to overrides orm write method.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		if vals.has_key('state') and vals['state'] == 'new_draft':
			vals.update({'color':0})
		if vals.has_key('state') and vals['state'] == 'draft':
			vals.update({'color':4})
		if vals.has_key('state') and vals['state'] == 'book':
			vals.update({'color':2})
		if vals.has_key('state') and vals['state'] == 'normal':
			vals.update({'color':7})
		if vals.has_key('state') and vals['state'] == 'close':
			vals.update({'color':9})
		if vals.has_key('state') and vals['state'] == 'sold':
			vals.update({'color':9})
		if vals.has_key('state') and vals['state'] == 'cancel':
			vals.update({'color':1})
		return super(account_asset_asset, self).write(vals)

	@api.onchange('parent_id')
	def parent_property_onchange(self):
		"""
			when you change Parent Property, this method will change
			address fields values accordingly.
		@param self: The object pointer
		"""
		if self.parent_id:
			self.street = self.parent_id.street or ''
			self.street2 = self.parent_id.street2 or ''
			self.township = self.parent_id.township or ''
			self.city = self.parent_id.city or ''
			self.state_id = self.parent_id.state_id.id or False
			self.zip = self.parent_id.zip or ''
			self.country_id = self.parent_id.country_id.id or False

	@api.onchange('gfa_feet')
	def sqft_to_meter(self):
		"""
			when you change GFA Feet, this method will change
			GFA Meter field value accordingly.
		@param self: The object pointer
		@return: Calculated GFA Feet.
		"""
		meter_val = 0.0
		if self.gfa_feet:
			meter_val = float(self.gfa_feet / 10.7639104)
		self.gfa_meter = meter_val

	@api.onchange('unit_price')
	def unit_price_calc(self):
		"""
			when you change Unit Price and GFA Feet fields value,
			this method will change Total Price and Purchase Value
			accordingly.
		@param self: The object pointer
		"""
		if self.unit_price and self.gfa_feet:
			self.total_price = float(self.unit_price * self.gfa_feet)
			self.value = float(self.unit_price * self.gfa_feet)
		if self.unit_price and not self.gfa_feet:
			raise ValidationError(_('Please Insert GFA(Sqft) Please'))

	@api.multi
	def edit_status(self):
		"""
			This method is used to change property state to book.
		@param self: The object pointer
		"""
		for rec in self:
			if not rec.property_manager:
				raise ValidationError(_('Please Insert Owner Name'))
		return self.write({'state': 'book'})

	@api.multi
	def edit_status_book(self):
		"""
			This method will open a wizard.
		@param self: The object pointer
		"""
		cr, uid, context = self.env.args
		context = dict(context)
		for rec in self:
			context.update({'edit_result':rec.id})
			self.env.args = cr, uid, misc.frozendict(context)
		return {
			'name': ('wizard'),
			'res_model': 'book.available',
			'type': 'ir.actions.act_window',
			'view_id': False,
			'view_mode': 'form',
			'view_type': 'form',
			'target':'new',
			'context':{'default_current_ids':context.get('edit_result')},
			}

	@api.multi
	def open_url(self):
		"""
			This Button method is used to open a URL
			according fields values.
		@param self: The object pointer
		"""
		for property_brw in self:
			if property_brw.lat and property_brw.lon:
				rep_address = str(property_brw.lat)+","+str(property_brw.lon)
				URL = "http://maps.google.com/?q=%s&ie=UTF8&z=18" % (rep_address)
				return {
					'name':'Go to website',
					'res_model':'ir.actions.act_url',
					'type':'ir.actions.act_url',
					'target':'current',
					'url': URL
					}
			if property_brw.street:
				address_path = (property_brw.street and (property_brw.street + ',') or ' ') + (property_brw.street2 and (property_brw.street2 + ',') or ' ') + (property_brw.city and (property_brw.city + ',') or ' ') + (property_brw.state_id.name and (property_brw.state_id.name + ',') or ' ') + (property_brw.country_id.name and (property_brw.country_id.name + ',') or ' ')
				rep_address = address_path.replace(' ', '+')
				URL = "http://maps.google.com/?q=%s&ie=UTF8&z=18" % (rep_address)
				return {
					'name':'Go to website',
					'res_model':'ir.actions.act_url',
					'type':'ir.actions.act_url',
					'target':'current',
					'url': URL
					}
			else:
				raise osv.except_osv(('No Address!'), ('No Address created for this Property!'))
		return True

	@api.multi
	def button_normal(self):
		"""
			This Button method is used to change property state to On Lease.
		@param self: The object pointer
		"""
		return self.write({'state':'normal'})

	@api.multi
	def button_sold(self):
		"""
			This Button method is used to change property state to Sold.
		@param self: The object pointer
		"""
		return self.write({'state':'sold'})

	@api.multi
	def button_close(self):
		"""
			This Button method is used to change property state to Sale.
		@param self: The object pointer
		"""
		return self.write({'state':'close'})

	@api.multi
	def button_cancel(self):
		"""
			This Button method is used to change property state to Cancel.
		@param self: The object pointer
		"""
		return self.write({'state':'cancel'})

	@api.multi
	def button_draft(self):
		"""
			This Button method is used to change property state to Available.
		@param self: The object pointer
		"""
		return self.write({'state':'draft'})

	@api.multi
	def create_purchase_installment(self):
		"""
			This Button method is used to create purchase installment
			information entries.
		@param self: The object pointer
		"""
		year_create = []
		for res in self:
			amount = res['purchase_price']
			if res['purchase_price'] == 0.0:
				raise Warning(_('Please Enter Valid Purchase Price'))
			starting_date_date = datetime.strptime(res['date'], DEFAULT_SERVER_DATE_FORMAT)
			starting_day = datetime.strptime(res['date'],DEFAULT_SERVER_DATE_FORMAT).day
			if not res['end_date']:
				raise Warning(_('Please Select End Date'))
			ending_date_date = datetime.strptime(res['end_date'], DEFAULT_SERVER_DATE_FORMAT)
			ending_day = datetime.strptime(res['end_date'], DEFAULT_SERVER_DATE_FORMAT).day
			if ending_date_date.date() < starting_date_date.date():
				raise Warning(_("Please Select End Date greater than purchase date"))
	#		method used to calculate difference in month between two dates
			def diff_month(d1, d2):
				return (d1.year - d2.year)*12 + d1.month - d2.month
			difference_month = diff_month(ending_date_date, starting_date_date)
			if difference_month == 0:
				amnt = amount
			else :
				if ending_date_date.day > starting_date_date.day:
					difference_month += 1
				amnt = amount/difference_month
			cr = self._cr
			cr.execute("SELECT date FROM cost_cost WHERE purchase_property_id=%s" % self._ids[0])
			exist_dates = cr.fetchall()
			date_add = self.date_addition(res['date'], res['end_date'], res['recurring_rule_type'])
			exist_dates = map(lambda x:x[0], exist_dates)
			result = list(set(date_add) - set(exist_dates))
			result.sort(key=lambda item:item, reverse=False)
			ramnt = amnt
			remain_amnt = 0.0
			for dates in result:
				remain_amnt = amount - ramnt
				remain_amnt_per = (remain_amnt/res['purchase_price'])*100
				if remain_amnt < 0 :
					remain_amnt = remain_amnt * -1
				if remain_amnt_per < 0:
					remain_amnt_per = remain_amnt_per * -1
				year_create.append((0, 0, {
										'currency_id': res.currency_id.id or False,
										'date':dates,
										'purchase_property_id':self._ids[0],
										'amount':amnt,
										'remaining_amount':remain_amnt,
										'rmn_amnt_per':remain_amnt_per,
										}))
				amount = remain_amnt
		return self.write({'purchase_cost_ids':year_create,'pur_instl_chck':True})

	@api.multi
	def date_addition(self, starting_date, end_date, period):
		date_list = []
		if period == 'monthly':
			while starting_date < end_date:
				date_list.append(starting_date)
				res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
				starting_date = res
			return date_list
		else:
			while starting_date < end_date:
				date_list.append(starting_date)
				res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
				starting_date = res
			return date_list

	@api.multi
	def genrate_payment_enteries(self):
		"""
			This Button method is used to generate property sale payment entries.
		@param self: The object pointer
		"""
		for data in self:
			amount = data.sale_price
			year_create = []
			payment_term_brw = self.env['account.payment.term'].browse(data.payment_term.id)
			pterm_list = payment_term_brw.compute(data.sale_price, data.sale_date)
			if amount == 0.0:
				raise Warning(_('Please Enter Valid Sale Price'))
			rmnt = 0.0
			for line in pterm_list:
				lst = list(line[0])
				remain_amnt = amount-lst[1]
				remain_amnt_per = (remain_amnt/data.sale_price)*100
				if remain_amnt < 0 :
					remain_amnt = remain_amnt * -1
				if remain_amnt_per < 0:
					remain_amnt_per = remain_amnt_per * -1
				year_create.append((0, 0, {
										'currency_id': data.currency_id.id or False,
										'date':lst[0],
										'sale_property_id':self._ids,
										'amount':lst[1],
										'remaining_amount':remain_amnt,
										'rmn_amnt_per':remain_amnt_per,
										}))
				amount = amount - lst[1]
			self.write({'sale_cost_ids':year_create,'sale_instl_chck':True})
		return True
