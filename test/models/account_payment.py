# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class AccountPaymentInherit(models.Model):
	_inherit = "account.payment"

	@api.one
	@api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
	def _compute_difference(self):
		if len(self.invoice_ids) == 0:
			return
		if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
			self.o_amount = self.amount - self._compute_total_invoices_amount()
		else:
			self.o_amount = self._compute_total_invoices_amount() - self.amount

	o_amount = fields.Monetary(string='Other Payment Amount', compute='_compute_difference', required=True)
	o_currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
	o_journal_id = fields.Many2one('account.journal', string='Other Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

	@api.multi
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconciliable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		for rec in self:

			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

			if any(inv.state != 'open' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

			# Use the right sequence to set the name
			if rec.payment_type == 'transfer':
				sequence_code = 'account.payment.transfer'
			else:
				if rec.partner_type == 'customer':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.customer.invoice'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.customer.refund'
				if rec.partner_type == 'supplier':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.supplier.refund'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.supplier.invoice'
			rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)

			# Create the journal entry
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
			move = rec._create_payment_entry(amount)
			
			
			# o_vals={
			# 	'state': 'posted',
			# 	'amount': rec.o_amount,
			# 	'journal_id': rec.o_journal_id.id,
			# 	'payment_type': 'inbound',
			# 	'communication':rec.communication,
			# 	'partner_id': rec.partner_id.id,
			# 	'payment_method_id': rec.payment_method_id.id,
			# }
			# self.env['account.payment'].create(o_vals)
			# In case of a transfer, the first journal entry created debited the source liquidity account and credited
			# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
			if rec.payment_type == 'transfer':
				transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
				transfer_debit_aml = rec._create_transfer_entry(amount)
				(transfer_credit_aml + transfer_debit_aml).reconcile()

			temp = rec._compute_total_invoices_amount()
			rec._create_payment_entry(rec.o_amount)


			inv = rec.env['account.payment'].create({
					'state': 'posted',
					'amount': abs(temp),
					'journal_id': rec.o_journal_id.id,
					'payment_type': 'inbound',
					'communication':rec.communication,
					'partner_id': rec.partner_id.id,
					'payment_method_id': rec.payment_method_id.id,
				})

			rec.write({'state': 'posted', 'move_name': move.name})


	# def _create_payment_entry(self, amount, journal=None):
	# 	""" Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
	# 		Return the journal entry.
	# 	"""
	# 	aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
	# 	invoice_currency = False
	# 	if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
	# 		#if all the invoices selected share the same currency, record the paiement in that currency too
	# 		invoice_currency = self.invoice_ids[0].currency_id
	# 	debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

	# 	if journal:
	# 		move = self.env['account.move'].create(self._get_move_vals(journal))
	# 	else:	
	# 		move = self.env['account.move'].create(self._get_move_vals())

	# 	#Write line corresponding to invoice payment
	# 	counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
	# 	counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
	# 	counterpart_aml_dict.update({'currency_id': currency_id})
	# 	counterpart_aml = aml_obj.create(counterpart_aml_dict)

	# 	#Reconcile with the invoices
	# 	if self.payment_difference_handling == 'reconcile' and self.payment_difference:
	# 		writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
	# 		amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
	# 		# the writeoff debit and credit must be computed from the invoice residual in company currency
	# 		# minus the payment amount in company currency, and not from the payment difference in the payment currency
	# 		# to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
	# 		total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
	# 		total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
	# 		if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
	# 			amount_wo = total_payment_company_signed - total_residual_company_signed
	# 		else:
	# 			amount_wo = total_residual_company_signed - total_payment_company_signed
	# 		# Align the sign of the secondary currency writeoff amount with the sign of the writeoff
	# 		# amount in the company currency
	# 		if amount_wo > 0:
	# 			debit_wo = amount_wo
	# 			credit_wo = 0.0
	# 			amount_currency_wo = abs(amount_currency_wo)
	# 		else:
	# 			debit_wo = 0.0
	# 			credit_wo = -amount_wo
	# 			amount_currency_wo = -abs(amount_currency_wo)
	# 		writeoff_line['name'] = _('Counterpart')
	# 		writeoff_line['account_id'] = self.writeoff_account_id.id
	# 		writeoff_line['debit'] = debit_wo
	# 		writeoff_line['credit'] = credit_wo
	# 		writeoff_line['amount_currency'] = amount_currency_wo
	# 		writeoff_line['currency_id'] = currency_id
	# 		writeoff_line = aml_obj.create(writeoff_line)
	# 		if counterpart_aml['debit']:
	# 			counterpart_aml['debit'] += credit_wo - debit_wo
	# 		if counterpart_aml['credit']:
	# 			counterpart_aml['credit'] += debit_wo - credit_wo
	# 		counterpart_aml['amount_currency'] -= amount_currency_wo
	# 	self.invoice_ids.register_payment(counterpart_aml)

	# 	#Write counterpart lines
	# 	if not self.currency_id != self.company_id.currency_id:
	# 		amount_currency = 0
	# 	liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
	# 	liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
	# 	aml_obj.create(liquidity_aml_dict)

	# 	move.post()
	# 	return move
