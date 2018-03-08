from odoo import models, fields, api, _, osv
import xlsxwriter
from odoo.exceptions import Warning
from datetime import timedelta, datetime
import babel
import calendar
import json
import StringIO
from odoo.tools import config, posix_to_ldml


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"

    def _report_name_to_report_model(self):
        return {
            'financial_report': 'account.financial.html.report',
            'generic_tax_report': 'account.generic.tax.report',
            'followup_report': 'account.followup.report',
            'bank_reconciliation': 'account.bank.reconciliation.report',
            'general_ledger': 'account.general.ledger',
            'aged_receivable': 'account.aged.receivable',
            'aged_payable': 'account.aged.payable',
            'coa': 'account.coa.report',
            'l10n_be_partner_vat_listing': 'l10n.be.report.partner.vat.listing',
            'l10n_be_partner_vat_intra': 'l10n.be.report.partner.vat.intra',
            'partner_ledger': 'account.partner.ledger',
            'tenancy_report': 'realestate.tenancy',
        }

    def _report_model_to_report_context(self):
        return {
            'account.financial.html.report': 'account.financial.html.report.context',
            'account.generic.tax.report': 'account.report.context.tax',
            'account.followup.report': 'account.report.context.followup',
            'account.bank.reconciliation.report': 'account.report.context.bank.rec',
            'account.general.ledger': 'account.context.general.ledger',
            'account.aged.receivable': 'account.context.aged.receivable',
            'account.aged.payable': 'account.context.aged.payable',
            'account.coa.report': 'account.context.coa',
            'l10n.be.report.partner.vat.listing': 'l10n.be.partner.vat.listing.context',
            'l10n.be.report.partner.vat.intra': 'l10n.be.partner.vat.intra.context',
            'account.partner.ledger': 'account.partner.ledger.context',
            'realestate.tenancy': 'realestate.context.tenancy',
        }