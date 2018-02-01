# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    @api.depends('amount', 'paid_amount')
    def _check_pay_amount(self):
        if self.amount != self.paid_amount:
            raise UserError(_("Please check Paid amount and Invoice amount"))

    @api.one
    @api.depends('invoice_payment_id')
    def _get_paid_amount(self):
        paid_amount = 0
        if self.invoice_payment_id:
            self.paid_amount = 0
            for invoice in self.invoice_payment_id:
                if invoice.payment_amount > invoice.opening_amount:
                    raise UserError(_("you can not set more then paid amount of payment"))
                paid_amount += invoice.payment_amount
            # if paid_amount > self.amount:
            #     raise UserError(_("you can not set more then paid amount of payment"))
            self.paid_amount = paid_amount

    invoice_payment_id = fields.One2many('mass.account.payment', 'mass_payment_id', string="Invoices")
    paid_amount = fields.Float(compute='_get_paid_amount', string="Paid Amount", store=True)
    payment_line_ids = fields.One2many('account.payment.line', 'payment_id', string='Move move_line_ids')
    total_due_amount = fields.Float('Total Unsettled Invocie')
    total_unsettled_invoice = fields.Float('Total Due Amount')
    payment_method = fields.Selection([
                        ('bank', 'Bank'),
                        ('check', 'Check')],
                        string='Payment Method',
                        default='bank')
    checkbook_no_id = fields.Many2one('check.book', string='Checkbook No')
    check_no = fields.Char('Check Number')
    check_type = fields.Selection([
                    ('manual', 'Manual'),
                    ('auto', 'Auto')], string='Check Type')

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            self.check_type = self.journal_id.check_type

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if self._context.get('other_journal_id'):
            journal = self._context['other_journal_id']
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'check_no': self.check_no,
            'payment_method': self.payment_method,
            'check_type': self.check_type,
            'checkbook_no_id': self.checkbook_no_id.id,
        }

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        journal = self.journal_id
        if self.payment_method == 'check' and journal.check_request \
                and journal.check_type == 'auto' and journal.check_book_ids:
            res = False
            for checkbook in journal.check_book_ids:
                res = True
                if checkbook.total_used_no < checkbook.to_no:
                    diff = (checkbook.to_no - checkbook.total_used_no)
                    if not diff or diff <= journal.remain_check:
                        res = False
                        if not checkbook.sent:
                            check_template = self.env.ref('mass_payment.email_template_checkbook_reminder_mail')
                            if check_template:
                                check_template.send_mail(journal.id, force_send=True)
                                checkbook.write({'sent': True})
            if not res:
                warning = {
                    'title': _('Warning'),
                    'message': 'Please order new check book'
                }
                return {
                    'warning': warning
                }

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        self._onchange_payment_method()
        return super(AccountPayment, self).copy(default)

    def _check_no(self, journal, check_book, check_no):
        CheckbookCancel = self.env['check.book.cancel']
        find_check_no = CheckbookCancel.search([
            ('bank_journal_id', '=', journal),
            ('check_book_no_id', '=', check_book),
            ('check_no', '=', check_no)])
        if find_check_no:
            check_no += 1
            self._check_no(journal, check_book, check_no)
        return check_no

    @api.model
    def create(self, vals):
        Journal = self.env['account.journal']
        if vals.get('payment_type') == 'outbound' and vals.get('payment_method') == 'check':
            journal = Journal.browse(vals['journal_id'])
            # checkbook = journal.check_book_ids[0]
            if journal.check_type == 'auto':
                res = False
                for checkbook in journal.check_book_ids:
                    if checkbook.total_used_no == 0:
                        check_no = checkbook.from_no
                        res = self._check_no(vals['journal_id'], checkbook.id, check_no)
                        checkbook.write({
                            'total_used_no': res
                        })
                        vals['check_no'] = res
                        vals['checkbook_no_id'] = checkbook.id
                        break
                    else:
                        if checkbook.total_used_no < checkbook.to_no:
                            checkno = (checkbook.total_used_no + 1)
                            res = self._check_no(vals['journal_id'], checkbook.id, checkno)
                            if res:
                                vals['check_no'] = res
                                vals['checkbook_no_id'] = checkbook.id
                                checkbook.write({
                                    'total_used_no': res
                                })
                                break
                            else:
                                continue
                            # vals['check_no'] = res
                if not res:
                    raise UserError(_('Check number reached its last number'))
        return super(AccountPayment, self).create(vals)

    @api.multi
    def payment_print(self):
        if self.payment_method == 'bank':
            return self.env['report'].get_action(self, 'mass_payment.report_transfer')
        elif self.payment_method == 'check':
            return self.env['report'].get_action(self, 'mass_payment.report_checkbook')

    @api.multi
    def payment_voucher_print(self):
        return self.env['report'].get_action(self, 'mass_payment.report_mass_payment')

    @api.onchange('partner_id', 'partner_type')
    def _onchange_partner(self):
        open_invoice_ids = []
        move_line_ids = []
        total_due_amount = 0.0
        total_unsettled_invoice = 0.0
        if self.partner_id and self.partner_type == 'customer':
            open_invoice_ids = self.env['account.invoice'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'open'),
                ('type', 'in', ['out_invoice', 'out_refund'])
            ])
            if open_invoice_ids:
                create_new = []
                for invoice in open_invoice_ids:
                    create_new += [(0, 0, {'invoice_id': invoice.id})]
                self.invoice_payment_id = create_new

            account_move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', self.partner_id.id),
                ('reconciled', '=', False),
                ('account_id.user_type_id.type', '=', 'receivable'),
            ])
            for line in account_move_lines:
                if line.debit > 0.0:
                    total_due_amount += abs(line.amount_residual)
                else:
                    total_unsettled_invoice += abs(line.amount_residual)
                rs = {
                    'name': line.move_id.name,
                    'type': line.credit and 'dr' or 'cr',
                    'line_id': line.id,
                    'account_id': line.account_id.id,
                    'date_original': line.date,
                    'date_due': line.date_maturity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'amount': abs(line.amount_residual),
                }
                move_line_ids.append(rs)

        elif self.partner_id and self.partner_type == 'supplier':
            open_invoice_ids = self.env['account.invoice'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'open'),
                ('type', 'in', ['in_invoice', 'in_refund'])
            ])
            if open_invoice_ids:
                create_new = []
                for invoice in open_invoice_ids:
                    create_new += [(0, 0, {'invoice_id': invoice.id})]
                self.invoice_payment_id = create_new

            account_move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', self.partner_id.id),
                ('reconciled', '=', False),
                ('account_id.user_type_id.type', '=', 'payable'),
            ])
            for line in account_move_lines:
                if line.credit > 0.0:
                    total_due_amount += abs(line.amount_residual)
                else:
                    total_unsettled_invoice += abs(line.amount_residual)
                rs = {
                    'name': line.move_id.name,
                    'type': line.credit and 'dr' or 'cr',
                    'line_id': line.id,
                    'account_id': line.account_id.id,
                    'date_original': line.date,
                    'date_due': line.date_maturity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'amount': abs(line.amount_residual),
                }
                move_line_ids.append(rs)
        self.payment_line_ids = move_line_ids
        self.total_due_amount = total_due_amount
        if total_unsettled_invoice > total_due_amount:
            self.total_unsettled_invoice = 0.0
        else:
            self.total_unsettled_invoice = abs(total_due_amount - total_unsettled_invoice)
        self.amount = total_due_amount

    @api.onchange('amount')
    def _onchange_payment(self):
        if not any(rec.payment_amount > 0.0 for rec in self.invoice_payment_id) and self.amount:
            # if self.amount:
            remain_amount = self.amount
            paid_amount = 0.0
            for invoice in self.invoice_payment_id:
                invoice.payment_amount = 0.0
                if remain_amount >= invoice.opening_amount and not invoice.payment_amount:
                    invoice.payment_amount = invoice.opening_amount
                    remain_amount -= invoice.opening_amount
                    paid_amount += invoice.payment_amount
                elif remain_amount:
                    invoice.payment_amount = remain_amount
                    remain_amount -= invoice.payment_amount
                    paid_amount += invoice.payment_amount

    @api.onchange('payment_line_ids')
    def _onchange_payment_line_ids(self):
        total_due_amount = 0.0
        if self.payment_line_ids and self.partner_type == 'customer':
            if self.partner_id:
                account_move_lines = self.env['account.move.line'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('reconciled', '=', False),
                    ('account_id.user_type_id.type', '=', 'receivable'),
                ])
                for line in account_move_lines:
                    if line.debit > 0.0:
                        total_due_amount += abs(line.amount_residual)
            debit_total = 0.0
            debit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'dr' and r.is_check)
            debit_total = sum(line.amount for line in debit_lines)
            if total_due_amount >= debit_total:
                self.amount = total_due_amount - debit_total
            elif total_due_amount < debit_total:
                self.amount = 0.0

        elif self.payment_line_ids and self.partner_type == 'supplier':
            if self.partner_id:
                account_move_lines = self.env['account.move.line'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('reconciled', '=', False),
                    ('account_id.user_type_id.type', '=', 'payable'),
                ])
                for line in account_move_lines:
                    if line.credit > 0.0:
                        total_due_amount += abs(line.amount_residual)
            credit_total = 0.0
            credit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'cr' and r.is_check)
            credit_total = sum(line.amount for line in credit_lines)
            if total_due_amount >= credit_total:
                self.amount = total_due_amount - credit_total
            elif total_due_amount < credit_total:
                self.amount = 0.0

    @api.multi
    def post(self):
        if self.payment_line_ids:
            if self.partner_type == 'supplier':
                # credit total
                credit_total = 0.0
                credit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'cr')
                credit_total = sum(line.amount for line in credit_lines)

                # debit total
                debit_total = 0.0
                debit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'dr')
                debit_total = sum(line.amount for line in debit_lines)

                if credit_total > debit_total:
                    raise UserError(_('You can not do payment because debit total is more than credit total'))

            elif self.partner_type == 'customer':
                debit_total = 0.0
                debit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'dr')
                debit_total = sum(line.amount for line in debit_lines)

                credit_total = 0.0
                credit_lines = self.payment_line_ids.filtered(lambda r: r.type == 'cr')
                credit_total = sum(line.amount for line in credit_lines)
                if debit_total > credit_total:
                    raise UserError(_('You can not do payment because credit total is more than debit total'))

            invoice_ids = []
            payment_lines = self.payment_line_ids.filtered(lambda r: r.is_check)
            move_lines = payment_lines.mapped('line_id')
            move_lines.reconcile()
            if self.amount > 0.0 and self.invoice_payment_id:
                paid_amount = 0
                for paid_invoice in self.invoice_payment_id:
                    paid_amount += paid_invoice.payment_amount
                    if paid_invoice.payment_amount and paid_invoice.invoice_id.state == 'open':
                        invoice_ids.append((4, paid_invoice.invoice_id.id, None))
                if paid_amount and paid_amount < self.amount:
                    payment_data = {
                        'invoice_ids': invoice_ids,
                    }
                    self.write(payment_data)
                    return super(AccountPayment, self).post()
                else:
                    payment_data = {
                        'invoice_ids': invoice_ids,
                    }
                    self.write(payment_data)
                    return super(AccountPayment, self).post()
            else:
                self.write({'state': 'posted'})
        else:
            if self.invoice_payment_id:
                invoice_ids = []
                paid_amount = 0
                for paid_invoice in self.invoice_payment_id:
                    paid_amount += paid_invoice.payment_amount
                    if paid_invoice.payment_amount and paid_invoice.invoice_id.state == 'open':
                        invoice_ids.append((4, paid_invoice.invoice_id.id, None))
                payment_data = {
                    'invoice_ids': invoice_ids,
                }
                self.write(payment_data)
                return super(AccountPayment, self).post()
            else:
                super(AccountPayment, self).post()


class MassAccountPayment(models.Model):
    _name = 'mass.account.payment'

    mass_payment_id = fields.Many2one('account.payment', string="Payment Ref")
    invoice_id = fields.Many2one('account.invoice', string="Invoice Number")
    date_due = fields.Date(related='invoice_id.date_due', relation='account.invoice', string='Due Date')
    date_invoice = fields.Date(related='invoice_id.date_invoice', relation='account.invoice', string='Invoice Date',)
    original_amount = fields.Monetary(related='invoice_id.amount_total', relation='account.invoice', string="Original Amount", currency_field='currency_id')
    opening_amount = fields.Monetary(related='invoice_id.residual', relation='account.invoice', string='Amount Due', currency_field='currency_id')
    payment_amount = fields.Monetary(string="Pay Amount")
    currency_id = fields.Many2one(related='invoice_id.currency_id', relation='res.currency', string='Currency')


class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'

    is_check = fields.Boolean('Check')
    name = fields.Char('Name')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    account_id = fields.Many2one('account.account', string='Account')
    type = fields.Selection([('dr', 'Debit'), ('cr', 'Credit')], string='Dr/Cr')
    payment_id = fields.Many2one('account.payment', string='Payment Ref')
    line_id = fields.Many2one('account.move.line', string='Move Line')
    date_original = fields.Date(related='line_id.date', string='Date', readonly=True)
    date_due = fields.Date(related='line_id.date_maturity', string='Due Date', readonly=1)
    amount = fields.Float('Amount')
    # amount_original = fields.function(_compute_balance, multi='dc', type='float', string='Original Amount', store=True, digits_compute=dp.get_precision('Account')),
    # amount_unreconciled = fields.function(_compute_balance, multi='dc', type=' store=True, digits_compute=dp.get_precision('Account')True,
