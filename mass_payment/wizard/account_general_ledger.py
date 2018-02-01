# -*- coding: utf-8 -*-

import base64
from cStringIO import StringIO
import xlsxwriter

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountGeneralLedgerReport(models.TransientModel):
    _inherit = 'account.report.general.ledger'

    partner_ids = fields.Many2many('res.partner', string='Partners')
    account_ids = fields.Many2many('account.account', string="Account")
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')

    def _print_report(self, data):
        data['form'].get('used_context', {}).update({
            'partner_ids': self.partner_ids.ids,
            'account_ids': self.account_ids.ids,
            'analytic_account_ids': self.analytic_account_ids,
        })
        return super(AccountGeneralLedgerReport, self)._print_report(data)

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))

        partner_condition = {
            'sql': " AND 1 IN %s ",
            'tpl_ids': (tuple([1, 2, 3]),)
        }
        partner_ids = self.env.context.get('partner_ids', [])
        if partner_ids:
            partner_condition = {
                'sql': " AND p.id IN %s ",
                'tpl_ids': (tuple(partner_ids),)
            }
        # analytic condition
        analytic_condition = {
            'sql': " AND 1 IN %s ",
            'analytic_ids': (tuple([1, 2, 3]),)
        }
        analytic_account_ids = self.env.context.get('analytic_account_ids', [])
        if analytic_account_ids:
            analytic_condition = {
                'sql': " AND aa.id IN %s ",
                'analytic_ids': (tuple(analytic_account_ids.ids),)
            }

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name, '' AS analytic_name \
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                LEFT JOIN account_analytic_account aa ON (l.analytic_account_id=aa.id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + partner_condition['sql'] + analytic_condition['sql'] + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + partner_condition['tpl_ids'] +  analytic_condition['analytic_ids'] + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name, aa.name AS analytic_name \
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            LEFT JOIN account_analytic_account aa ON (l.analytic_account_id=aa.id) \
            WHERE l.account_id IN %s''' + partner_condition['sql'] + analytic_condition['sql'] + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, aa.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + partner_condition['tpl_ids'] + analytic_condition['analytic_ids'] + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    @api.multi
    def check_report_excel(self):
        self.ensure_one()
        row_data = self.check_report()

        data = row_data.get('data', {})
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        # records = self.env[data['model']].browse(data.get('ids', []))
        self.model = self._inherit
        # self.model = self.env.context.get('active_model')
        # docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

        # accounts = self if self.model == 'account.account' else self.env['account.account'].search([])
        accounts = self.account_ids
        if self.model == 'account.account':
            accounts = self
        elif not accounts:
            accounts = self.env['account.account'].search([])
        accounts_res = self.with_context(
            data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, init_balance, sortby, display_account)

        # doc_ids = docids
        # doc_model = self.model
        # data = data['form']
        # docs = self
        # Accounts = accounts_res
        print_journal = codes

        #
        # Design Your Excel File HERE
        #

        company = self.env.user.company_id

        # Each Journal in Separate Sheet

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        # worksheet = workbook.add_worksheet(_('%s - General Ledger') % company.name)
        worksheet = workbook.add_worksheet(_('General Ledger'))
        # Styles

        style_bold_border_center = workbook.add_format({
            'text_wrap': 1,
            'valign': 'vjustify',
            'border': True,
            'bold': True,
            'align': 'center',
        })

        style_bold_font_border = workbook.add_format({
            'valign': 'vjustify',
            'bold': True,
            'align': 'center',
            'border': True})

        style_bold_font = workbook.add_format({
            'valign': 'vjustify',
            'bold': True,
            'align': 'center',
            })
        # style_border = workbook.add_format({
        #     'text_wrap': 1,
        #     'valign': 'vjustify',
        #     'border': True
        # })

        # style_border_right =  workbook.add_format({
        #     'text_wrap': 1,
        #     'valign': 'vjustify',
        #     'border': True,
        #     'align': 'right'
        # })

        row = 1
        col = 0
        worksheet.merge_range(row, col + 8, row, col, _('%s: General Ledger') % company.name, style_bold_font)
        row += 2
        col = 0
        worksheet.merge_range(row, col, row, col + 3, _('Journals'), style_bold_border_center)
        col += 4
        worksheet.merge_range(row, col, row, col + 1, _('Display Account'), style_bold_border_center)
        col += 2
        worksheet.merge_range(row, col, row, col + 2, _('Target Moves:'), style_bold_border_center)
        row += 1
        col = 0
        worksheet.merge_range(row, col, row, col + 3, ', '.join([lt or '' for lt in print_journal]))
        col += 4
        if display_account == 'all':
            worksheet.merge_range(row, col, row, col + 1, _('All accounts'))
        if display_account == 'movement':
            worksheet.merge_range(row, col, row, col + 1, _('With movements'))
        if display_account == 'not_zero':
            worksheet.merge_range(row, col, row, col + 1, _('With balance not equal to zero'))
        col += 2
        if data['form']['target_move'] == 'all':
            worksheet.merge_range(row, col, row, col + 3, _('All Entries'))
        if data['form']['target_move'] == 'posted':
            worksheet.merge_range(row, col, row, col + 3, _('All Posted Entries'))

        col = 0
        row += 2
        worksheet.write(row, col, _('Date'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('JRNL'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Partner'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Ref'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Move'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Entry Label'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Debit'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Credit'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Balance'), style_bold_font_border)
        col += 1
        worksheet.write(row, col, _('Analytic Account'), style_bold_font_border)
        col += 1
        for acc in accounts_res:
            col = 0
            row += 1
            worksheet.merge_range(row, col, row, col + 5, _(acc.get('code') + " " + acc.get('name')), style_bold_font)
            col += 6
            worksheet.write(row, col, acc.get('debit'), style_bold_font)
            col += 1
            worksheet.write(row, col, acc.get('credit'), style_bold_font)
            col += 1
            worksheet.write(row, col, acc.get('balance'), style_bold_font)
            for move in acc.get('move_lines'):
                row += 1
                col = 0
                worksheet.write(row, col, move.get('ldate'))
                col += 1
                worksheet.write(row, col, move.get('lcode'))
                col += 1
                worksheet.write(row, col, move.get('partner_name'))
                col += 1
                worksheet.write(row, col, move.get('lref'))
                col += 1
                worksheet.write(row, col, move.get('move_name'))
                col += 1
                worksheet.write(row, col, move.get('lname'))
                # col += 1
                # worksheet.write(row, col, move.get('analytic_name'))
                col += 1
                worksheet.write(row, col, move.get('debit'))
                col += 1
                worksheet.write(row, col, move.get('credit'))
                col += 1
                worksheet.write(row, col, move.get('balance'))
                col += 1
                worksheet.write(row, col, move.get('analytic_name'))
            row += 1
            col = 0
            worksheet.merge_range(row, col, row, col + 8, "")

        workbook.close()
        file_base = base64.b64encode(fp.getvalue())
        fp.close()

        output = self.env['v.excel.output'].create({
            'name': 'GL Report',
            'filename': file_base
        })
        return output.download()
