# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class property_account_category(models.Model):
    _name = "property.account.category"

    name = fields.Char('Category Name')
    income_acc_id = fields.Many2one('account.account', 'Income Account', help='Income Account of Property.')
    expenses_acc_id = fields.Many2one('account.account', 'Expense Account', help='Expenses Account of Property.')
    discount_acc_id = fields.Many2one('account.account', 'Discount Account', help='Discount Account of Property.')
    vendor_payable_acc_id = fields.Many2one('account.account', 'Vendor Payable Account', help='Vendor Payable Account')
    customer_receivable_acc_id = fields.Many2one('account.account', 'Customer Receivable Account',
                                                 help='Customer Receivable Account')

class account_asset_asset(models.Model):
    _inherit = "account.asset.asset"

    property_account_category_id = fields.Many2one('property.account.category', 'Property Account Category',
                                                   help='Property Account Category.')
    discount_acc_id = fields.Many2one('account.account', 'Discount Account', help='Discount Account of Property.')

    @api.onchange('property_account_category_id')
    def onchange_property_account_category_id(self):
        """
        This Method is used to set property related fields value,
        on change of property.
        @param self: The object pointer
        """
        if self.property_account_category_id:
            self.income_acc_id = self.property_account_category_id.income_acc_id and self.property_account_category_id.income_acc_id.id or False
            self.expense_acc_id = self.property_account_category_id.expenses_acc_id and self.property_account_category_id.expenses_acc_id.id or False
            self.discount_acc_id = self.property_account_category_id.discount_acc_id and self.property_account_category_id.discount_acc_id.id or False



class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'

    property_account_category_id = fields.Many2one('property.account.category', 'Property Account Category',
                                                   help='Propert Account Category.')

    @api.onchange('property_account_category_id')
    def onchange_property_account_category_id(self):
        """
        This Method is used to set property related fields value,
        on change of property.
        @param self: The object pointer
        """
        if self.property_account_category_id:
            self.property_account_receivable_id = self.property_account_category_id.customer_receivable_acc_id and self.property_account_category_id.customer_receivable_acc_id.id or False
            self.property_account_payable_id = self.property_account_category_id.vendor_payable_acc_id and self.property_account_category_id.vendor_payable_acc_id.id or False


class property_case_type(models.Model):
    _name = "property.case.type"

    name = fields.Char('Name', size=50, required=True)


class property_case(models.Model):
    _name = "property.case"

    note = fields.Text('Remarks')
    name = fields.Char('Reference', size=60)
    issue_date = fields.Date('Issuance Date')
    type_id = fields.Many2one('property.case.type', 'Type')
    property_id = fields.Many2one('account.asset.asset', 'Property')
    tenancy_id = fields.Many2one('account.analytic.account', 'Tenancy')


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    case_ids = fields.One2many('property.case', 'tenancy_id', 'Cases')


class tenancy_rent_schedule(models.Model):
    _inherit = "tenancy.rent.schedule"

    case_id = fields.Many2one('property.case','Case')
