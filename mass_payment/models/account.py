# -*- encoding: UTF-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    check_no = fields.Char('Check Number')
    check_type = fields.Selection([
                    ('manual', 'Manual'),
                    ('auto', 'Auto')], string='Check Type')
    payment_method = fields.Selection([
                        ('bank', 'Bank'),
                        ('check', 'Check')],
                        string='Payment Method')
    checkbook_no_id = fields.Many2one('check.book', string='Checkbook No')
    # journal_type = fields.Selection(related='journal_id.type', string='Journal Type')
    # journal_type = fields.Selection([
    #         ('sale', 'Sale'),
    #         ('purchase', 'Purchase'),
    #         ('cash', 'Cash'),
    #         ('bank', 'Bank'),
    #         ('general', 'Miscellaneous'),
    #     ], string='Type')
    is_check = fields.Boolean('Is Check?')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', states={'posted': [('readonly', True)]}, )

    # @api.onchange('journal_id')
    # def _onchange_journal_id(self):
    #     res = {}
    #     if self.journal_id:
    #         warning = {}
    #         self.journal_type = self.journal_id.type
    #         self.check_type = self.journal_id.check_type
    #         # if self.journal_id.type == 'bank':
    #         if self.journal_id:
    #             self.check_type = self.journal_id.check_type
    #             if self.journal_id.type == 'bank':
    #                 warning = {
    #                     'title': _('Warning'),
    #                     'message': _('You have to select payment method.')
    #                 }
    #         if warning:
    #             res['warning'] = warning
    #     return res

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

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        res = {}
        self.is_check = False
        self.check_type = False
        if self.journal_id and self.journal_id.type == 'bank':
            warning = {}
            self.check_type = self.journal_id.check_type
            credit_account_id = self.journal_id.default_credit_account_id
            line = self.line_ids.filtered(lambda l: l.account_id == credit_account_id and l.credit > 0.0)
            if line and self.journal_id.check_request:
                self.is_check = True
                # self.payment_method = 'check'
                # if self.journal_id.type == 'bank':
                warning = {
                    'title': _('Warning'),
                    'message': _('You have to select payment method.')
                }
                res['warning'] = warning
        return res

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
        if self._context.get('invoice'):
            vals.update({
                'invoice_id': self._context['invoice'].id,
            })
        Journal = self.env['account.journal']
        if vals.get('payment_method') == 'check' and vals.get('is_check') and vals.get('check_type') == 'auto':
            journal = Journal.browse(vals['journal_id'])
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
        return super(AccountMove, self).create(vals)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_officer = fields.Char('Bank Officer')
    bank_officer_design = fields.Char('Bank Officer Designation')
    bank_branch = fields.Char('Bank Branch')
    # authorize_sign_ids = fields.Many2many(
    #                         'res.users',
    #                         'account_journal_user_sing_rel',
    #                         'journal_id',
    #                         'authorize_sing_id',
    #                         string='Authorize Signatories')
    authorize_sign_id = fields.Many2one(
                            'res.users',
                            string='Authorize Signatories')
    check_request = fields.Boolean('Check Book Request Notification')
    check_type = fields.Selection([
                    ('manual', 'Manual'),
                    ('auto', 'Auto')],
                    string='Type',
                    required=True, default='manual')
    check_book_ids = fields.One2many(
                        'check.book',
                        'journal_id',
                        string='Checkbooks')
    check_email = fields.Char(
                    'Check Request Responsible',
                    help='Mail send to this email')
    remain_check = fields.Integer(
                    'Remain Check Number to Notify',
                    required=True,
                    default=0,
                    help='Give number of check to remain for email send')
    top_margin = fields.Float('Top Margin')
    bottom_margin = fields.Float('Bottom Margin')
    right_margin = fields.Float('Right Margin')
    left_margin = fields.Float('Left Margin')


class CheckBook(models.Model):
    _name = 'check.book'

    name = fields.Char('Check Book No')
    journal_id = fields.Many2one('account.journal', string='Journal')
    total_used_no = fields.Integer('User Check Number', default=0)
    from_no = fields.Integer('From')
    to_no = fields.Integer('To')
    sent = fields.Boolean('Sent')


class CheckBookCancel(models.Model):
    _name = 'check.book.cancel'
    _rec_name = 'check_no'

    bank_journal_id = fields.Many2one('account.journal', string='Bank', required=True)
    check_book_no_id = fields.Many2one('check.book', 'Check Book No', required=True)
    check_no = fields.Char('Check Number', required=True)
    cancel_reason = fields.Text('Cancel Reason', required=True)
    # state = fields.Selection([
    #                 ('draft', 'New'),
    #                 ('confirm', 'Confirm'),
    #                 ('cancel', 'Cancelled'),
    #                 ('done', 'Done')], string='State')

    @api.model
    def create(self, vals):
        AccountPayment = self.env['account.payment']
        AccountMove = self.env['account.move']

        payments = AccountPayment.search([('check_no', '=', vals['check_no'])])
        moves = AccountMove.search([('check_no', '=', vals['check_no'])])
        if payments or moves:
            raise UserError(_('You can not cancel check which used in payment or transcation!'))
        return super(CheckBookCancel, self).create(vals)
