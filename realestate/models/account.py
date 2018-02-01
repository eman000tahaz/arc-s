# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
	_inherit = "account.move"
	_description = "Account Entry"

	schedule_date = fields.Date('Schedule Date',help='Rent Schedule Date.')
	source = fields.Char('Source', help='Source from where account move created.')

	@api.multi
	def assert_balanced(self):
		if not self.ids:
			return True
		prec = self.env['decimal.precision'].precision_get('Account')
		self._cr.execute("""\
			SELECT	  move_id
			FROM		account_move_line
			WHERE	   move_id in %s
			GROUP BY	move_id
			HAVING	  abs(sum(debit) - sum(credit)) > %s
			""", (tuple(self.ids), 10 ** (-max(5, prec))))
		self._cr.fetchall()
		if len(self._cr.fetchall()) != 0:
			raise UserError(_("Cannot create unbalanced journal entry."))
		return True


class account_move_line(models.Model):
	_inherit = "account.move.line"

	property_id = fields.Many2one('account.asset.asset', 'Property', help='Property Name.')


class account_payment(models.Model):
	_inherit = 'account.payment'

	tenancy_id = fields.Many2one('account.analytic.account', 'Tenancy', help='Tenancy Name.')
	property_id = fields.Many2one('account.asset.asset', 'Property', help='Property Name.')
	# rent_schedule_id = fields.Many2one('tenancy.rent.schedule','Rent',help='Rent Chedule.')

	@api.model
	def create(self,vals):
		res = super(account_payment,self).create(vals)
		if res and res.id and res.tenancy_id and res.tenancy_id.id:
			if res.payment_type == 'inbound':
				res.tenancy_id.write({'acc_pay_dep_rec_id':res.id})
			if res.payment_type == 'outbound':
				res.tenancy_id.write({'acc_pay_dep_ret_id':res.id})
		return res

	@api.multi
	def back_to_tenancy(self):
		"""
			This method will open a Tenancy form view.
		@param self: The object pointer
		@param context: A standard dictionary for contextual values
		"""
		for vou_brw in self:
			open_move_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_analytic_view_form')[1]
			tenancy_id = vou_brw.tenancy_id and vou_brw.tenancy_id.id
			if tenancy_id:
				return {
					'view_type': 'form',
					'view_id': open_move_id,
					'view_mode': 'form',
					'res_model': 'account.analytic.account',
					'res_id':tenancy_id,
					'type': 'ir.actions.act_window',
					'target': 'current',
					'context': self._context,
					}
			else:
				return True

#	Gives Credit amount line
	def _get_counterpart_move_line_vals(self, invoice=False):
		vals = super(account_payment, self)._get_counterpart_move_line_vals(invoice=invoice)
		if vals and self.tenancy_id and self.tenancy_id.id:
			if self.payment_type in ('inbound','outbound'):
				vals.update({'analytic_account_id':False})
		return vals

#	Gives Debit amount line
	def _get_liquidity_move_line_vals(self, amount):
		vals = super(account_payment, self)._get_liquidity_move_line_vals(amount)
		if vals and self.tenancy_id and self.tenancy_id.id:
			if self.payment_type in ('inbound','outbound'):
				vals.update({'analytic_account_id':self.tenancy_id.id})
		return vals

	def _create_payment_entry(self, amount):
		move = super(account_payment, self)._create_payment_entry(amount)
		if move and move.id and self.property_id and self.property_id.id:
			move.write({'asset_id':self.property_id.id or False,'source':self.tenancy_id.name or False})
		return move

class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	property_id = fields.Many2one('account.asset.asset', 'Property', help='Property Name.')

	@api.multi
	def action_move_create(self):
		res = super(AccountInvoice,self).action_move_create()
		for inv_rec in self:
			if inv_rec.move_id and inv_rec.move_id.id:
				inv_rec.move_id.write({'asset_id':inv_rec.property_id.id or False,'ref':'Maintenance Invoice','source':inv_rec.property_id.name or False})
		return res
