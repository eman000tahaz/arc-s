from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class tenancy_report(models.AbstractModel):
    _name = "realestate.tenancy"
    _description = "Tenancy Report"

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        currency_id = self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    @api.model
    def get_lines(self, context_id, line_id=None):
        lines = []
        accounts = self.env['account.analytic.account'].search([('is_property','=','True'), ('ten_date', '>=', context_id.date_from), ('ten_date', '<=', context_id.date_to)])
        for account in accounts:
            if account.sched == 'chosen_date':
                st_date = account.sched_date
            else:
                st_date = account.date_start

            dic = {
                'unfoldable': False,
                'unfolded': None,
                'name': account.name, 
                'level': 2, 
                'footnotes': {},
                #'colspan': 4,
                'type': 'line',  
                'id': account.id, 
                'columns': [str(account.ten_date), str(account.name), str(account.property_id.name), str(account.tenant_id.name), st_date, str(account.date), str(account.rent)] 
            }

            lines.append(dic)    
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print context_id
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
        print "                         "
   #      dic = {
			# 	'unfoldable': True, 
			# 	'unfolded': None, 
			# 	'name': u'100000 Fixed Asset Account', 
			# 	'level': 2, 
			# 	'colspan': 4, 
			# 	'footnotes': {}, 
			# 	'type': 'line', 
			# 	'id': 2, 
			# 	'columns': ['', u'$ 0.00', u'$ 1,250.00', u'$ -1,250.00']
			# }
   #      dic2 = {
   #          'name': u'Initial Balance', 
   #          'level': 1, 
   #          'footnotes': {}, 
   #          'type': 'initial_balance', 
   #          'id': 7, 
   #          'columns': ['', '', '', '', u'$ 7,035.00', u'$ 0.00', u'$ 7,035.00'] 
   #      }
   #      lines.append(dic1)
   #      lines.append(dic2)
        return lines

    # @api.model
    # def _lines(self, line_id=None):
    #     lang_code = self.env.lang or 'en_US'
    #     lang = self.env['res.lang']
    #     lang_id = lang._lang_get(lang_code)
    #     date_format = lang_id.date_format
    #     lines = []
    #     context = self.env.context
    #     company_id = context.get('company_id') or self.env.user.company_id
    #     grouped_accounts = self.with_context(date_from_aml=context['date_from'], date_from=context['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(context['date_from'], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
    #     sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
    #     unfold_all = context.get('print_mode') and not context['context_id']['unfolded_accounts']
    #     for account in sorted_accounts:
    #         debit = grouped_accounts[account]['debit']
    #         credit = grouped_accounts[account]['credit']
    #         balance = grouped_accounts[account]['balance']
    #         amount_currency = '' if not account.currency_id else self._format(grouped_accounts[account]['amount_currency'], currency=account.currency_id)
    #         lines.append({
    #             'id': account.id,
    #             'type': 'line',
    #             'name': account.code + " " + account.name,
    #             'footnotes': self.env.context['context_id']._get_footnotes('line', account.id),
    #             'columns': [amount_currency, self._format(debit), self._format(credit), self._format(balance)],
    #             'level': 2,
    #             'unfoldable': True,
    #             'unfolded': account in context['context_id']['unfolded_accounts'] or unfold_all,
    #             'colspan': 4,
    #         })
    #         if account in context['context_id']['unfolded_accounts'] or unfold_all:
    #             initial_debit = grouped_accounts[account]['initial_bal']['debit']
    #             initial_credit = grouped_accounts[account]['initial_bal']['credit']
    #             initial_balance = grouped_accounts[account]['initial_bal']['balance']
    #             initial_currency = '' if not account.currency_id else self._format(grouped_accounts[account]['initial_bal']['amount_currency'], currency=account.currency_id)
    #             domain_lines = [{
    #                 'id': account.id,
    #                 'type': 'initial_balance',
    #                 'name': _('Initial Balance'),
    #                 'footnotes': self.env.context['context_id']._get_footnotes('initial_balance', account.id),
    #                 'columns': ['', '', '', initial_currency, self._format(initial_debit), self._format(initial_credit), self._format(initial_balance)],
    #                 'level': 1,
    #             }]
    #             progress = initial_balance
    #             amls = amls_all = grouped_accounts[account]['lines']
    #             too_many = False
    #             if len(amls) > 80 and not context.get('print_mode'):
    #                 amls = amls[:80]
    #                 too_many = True
    #             used_currency = self.env.user.company_id.currency_id
    #             for line in amls:
    #                 if self.env.context['cash_basis']:
    #                     line_debit = line.debit_cash_basis
    #                     line_credit = line.credit_cash_basis
    #                 else:
    #                     line_debit = line.debit
    #                     line_credit = line.credit
    #                 line_debit = line.company_id.currency_id.compute(line_debit, used_currency)
    #                 line_credit = line.company_id.currency_id.compute(line_credit, used_currency)
    #                 progress = progress + line_debit - line_credit
    #                 currency = "" if not line.currency_id else self.with_context(no_format=False)._format(line.amount_currency, currency=line.currency_id)
    #                 name = []
    #                 name = line.name and line.name or ''
    #                 if line.ref:
    #                     name = name and name + ' - ' + line.ref or line.ref
    #                 if len(name) > 35 and not self.env.context.get('no_format'):
    #                     name = name[:32] + "..."
    #                 partner_name = line.partner_id.name
    #                 if partner_name and len(partner_name) > 35  and not self.env.context.get('no_format'):
    #                     partner_name = partner_name[:32] + "..."
    #                 domain_lines.append({
    #                     'id': line.id,
    #                     'type': 'move_line_id',
    #                     'move_id': line.move_id.id,
    #                     'action': line.get_model_id_and_name(),
    #                     'name': line.move_id.name if line.move_id.name else '/',
    #                     'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', line.id),
    #                     'columns': [datetime.strptime(line.date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), name, partner_name, currency,
    #                                 line_debit != 0 and self._format(line_debit) or '',
    #                                 line_credit != 0 and self._format(line_credit) or '',
    #                                 self._format(progress)],
    #                     'level': 1,
    #                 })
    #             domain_lines.append({
    #                 'id': account.id,
    #                 'type': 'o_account_reports_domain_total',
    #                 'name': _('Total '),
    #                 'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', account.id),
    #                 'columns': ['', '', '', amount_currency, self._format(debit), self._format(credit), self._format(balance)],
    #                 'level': 1,
    #             })
    #             if too_many:
    #                 domain_lines.append({
    #                     'id': account.id,
    #                     'domain': "[('id', 'in', %s)]" % amls_all.ids,
    #                     'type': 'too_many',
    #                     'name': _('There are more than 80 items in this list, click here to see all of them'),
    #                     'footnotes': {},
    #                     'colspan': 8,
    #                     'columns': [],
    #                     'level': 3,
    #                 })
    #             lines += domain_lines

    #     if len(context['context_id'].journal_ids) == 1 and context['context_id'].journal_ids.type in ['sale', 'purchase'] and not line_id:
    #         total = self._get_journal_total()
    #         lines.append({
    #             'id': 0,
    #             'type': 'total',
    #             'name': _('Total'),
    #             'footnotes': {},
    #             'columns': ['', '', '', '', self._format(total['debit']), self._format(total['credit']), self._format(total['balance'])],
    #             'level': 1,
    #             'unfoldable': False,
    #             'unfolded': False,
    #         })
    #         lines.append({
    #             'id': 0,
    #             'type': 'line',
    #             'name': _('Tax Declaration'),
    #             'footnotes': {},
    #             'columns': ['', '', '', '', '', '', ''],
    #             'level': 1,
    #             'unfoldable': False,
    #             'unfolded': False,
    #         })
    #         lines.append({
    #             'id': 0,
    #             'type': 'line',
    #             'name': _('Name'),
    #             'footnotes': {},
    #             'columns': ['', '', '', '', _('Base Amount'), _('Tax Amount'), ''],
    #             'level': 2,
    #             'unfoldable': False,
    #             'unfolded': False,
    #         })
    #         for tax, values in self._get_taxes().items():
    #             lines.append({
    #                 'id': tax.id,
    #                 'name': tax.name + ' (' + str(tax.amount) + ')',
    #                 'type': 'tax_id',
    #                 'footnotes': self.env.context['context_id']._get_footnotes('tax_id', tax.id),
    #                 'unfoldable': False,
    #                 'columns': ['', '', '', '', values['base_amount'], values['tax_amount'], ''],
    #                 'level': 1,
    #             })

    #     print "                    "
    #     print "                    "
    #     print "                    "
    #     print "                    "
    #     print "                    "

    #     print lines
    #     print "                    "
    #     print "                    "
    #     print "                    "
    #     print "                    "
    #     print "                    "

    #     return lines


    @api.model
    def get_title(self):
        return _('Tenancy Report')

    @api.model
    def get_name(self):
        return 'tenancy_report'

    @api.model
    def get_report_type(self):
        return self.env.ref('account_reports.account_report_type_date_range_no_comparison')

    @api.model
    def get_template(self):
        return 'account_reports.report_financial'


class realestate_context_tenancy(models.TransientModel):
    _name = "realestate.context.tenancy"
    _description = "A particular context for the tenancy"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_accounts'
    unfolded_accounts = fields.Many2many('account.analytic.account', 'context_to_account', string='Unfolded lines')
    
    def get_report_obj(self):
        return self.env['realestate.tenancy']

    def get_columns_names(self):
        return [_("Date"), _("Tenancy"), _("Property"), _("Tenant Name"), _("Start Date"), _("Expire Date"), _("Rent")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "text", "text", "date", "date", "number"]
