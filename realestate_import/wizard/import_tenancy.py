# -*- coding: utf-8 -*-
import xlrd
import base64
import datetime

from odoo import api, fields, models


class ImportTenancy(models.TransientModel):
    _name = 'import.tenancy'

    file = fields.Binary('File')
    filename = fields.Char('Filename')

    @api.multi
    def import_tenancy(self):
        self.ensure_one()
        tenancy = self.env['account.analytic.account']
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)
                portfolio = data[0]
                building = data[1]
                building_no = data[2]
                prop = data[3]
                prop_no = data[4]
                prop_type = data[5]
                street = data[6]
                renter = data[7]
               	date = data[8]
               	start_date = data[9]
               	end_date = data[10]
               	rent = data[11]
               	discount = data[12]
               	balance = data[13]


                if portfolio:
                  portfolio_id = self.env['realestate.wallet'].search([('name', '=', portfolio.strip())])
                  if not portfolio_id:
                    portfolio_id = self.env['realestate.wallet'].create({
                                                                    'name': portfolio,
                                                                  })
                else:
                  portfolio_id = False

                
                if building:
                  building_id = self.env['account.asset.asset'].search([('name', '=', building.strip())])
                  if not building_id:
                    prop_acc_cat_ids = self.env['property.account.category'].search([])
                    if prop_acc_cat_ids:
                      cat = prop_acc_cat_ids[0]
                    else:
                      income_acc = self.env['account.account'].search([('code', '=', '101600')])
                      expenses_acc = self.env['account.account'].search([('code', '=', '220000')])
                      vendor_acc = self.env['account.account'].search([('code', '=', '111100')])
                      customer_acc = self.env['account.account'].search([('code', '=', '101200')])
                      discount_acc = self.env['account.account'].search([('code', '=', '101000')])
          
                      cat = self.env['property.account.category'].create({
                                                                    'name': 'property cat. 1',
                                                                    'income_acc_id': income_acc,
                                                                    'expenses_acc_id': expenses_acc,
                                                                    'vendor_payable_acc_id': vendor_acc,
                                                                    'customer_receivable_acc_id': customer_acc,
                                                                    'discount_acc_id':discount_acc,
                                                                  })
               			
                    prop_commession_ids = self.env['property.commession'].search([])
                    if prop_commession_ids:
                      com =prop_commession_ids[0]
                    else:
                      journal = self.env['account.journal'].search([('name', '=', 'Cash')])
                      com = self.env['property.commession'].create({
                                                              'name': 'commession 10%',
                                                              'value': 10.0,
                                                              'journal_id': journal,
                                                            })
                    
                    country_id = self.env['res.country'].search([('name', '=', 'kuwait')])
                    building_val = {
                                    'name': building,
                                    'wallet_id': portfolio_id.id,
                                    'street': street,
                                    'city': 'kuwait',
                                    'country_id': country_id.id,
                                    'type_id': 'building',
                                    'property_manager': 1,
                                    'property_account_category_id': cat.id,
                                    'property_commession': com.id,
                                    'discount_acc_id': cat.discount_acc_id.id,
                                    'income_acc_id': cat.income_acc_id.id,
                                    'expense_acc_id': cat.expenses_acc_id.id,
                                    'value':0,
                                  }

                    building_id = self.env['account.asset.asset'].create(building_val)
                else:
                  building_id = False

                
                if prop:
                  prop_id = self.env['account.asset.asset'].search([('name', '=', prop.strip())])
                  if not prop_id:
                    prop_acc_cat_ids = self.env['property.account.category'].search([])
                    if prop_acc_cat_ids:
                      cat = prop_acc_cat_ids[0]
                    else:
                      income_acc = self.env['account.account'].search([('code', '=', '101600')])
                      expenses_acc = self.env['account.account'].search([('code', '=', '220000')])
                      vendor_acc = self.env['account.account'].search([('code', '=', '111100')])
                      customer_acc = self.env['account.account'].search([('code', '=', '101200')])
                      discount_acc = self.env['account.account'].search([('code', '=', '101000')])
          
                      cat = self.env['property.account.category'].create({
                                                                    'name': 'property cat. 1',
                                                                    'income_acc_id': income_acc,
                                                                    'expenses_acc_id': expenses_acc,
                                                                    'vendor_payable_acc_id': vendor_acc,
                                                                    'customer_receivable_acc_id': customer_acc,
                                                                    'discount_acc_id':discount_acc,
                                                                  })
                    
                    prop_commession_ids = self.env['property.commession'].search([])
                    if prop_commession_ids:
                      com =prop_commession_ids[0]
                    else:
                      journal = self.env['account.journal'].search([('name', '=', 'Cash')])
                      com = self.env['property.commession'].create({
                                                              'name': 'commession 10%',
                                                              'value': 10.0,
                                                              'journal_id': journal,
                                                            })
                    
                    country_id = self.env['res.country'].search([('name', '=', 'kuwait')])
                    prop_val = {
                                    'name': prop,
                                    'parent_id': building_id.id or False,
                                    'wallet_id': portfolio_id.id or False,
                                    'street': street,
                                    'city': 'kuwait',
                                    'country_id': country_id.id,
                                    'type_id': prop_type,
                                    'property_manager': 1,
                                    'property_account_category_id': cat.id,
                                    'property_commession': com.id,
                                    'discount_acc_id': cat.discount_acc_id.id,
                                    'income_acc_id': cat.income_acc_id.id,
                                    'expense_acc_id': cat.expenses_acc_id.id,
                                    'value':0,
                                  }

                    prop_id = self.env['account.asset.asset'].create(prop_val)

                rent_type = self.env['rent.type'].search([('name', '=', '1'), ('renttype', '=', 'Month')])
                if not rent_type:
                  rent_type = self.env['rent.type'].create({
                                            'name': 1,
                                            'renttype': 'Month',
                                          })

                tenant = self.env['tenant.partner'].search([('name', '=', renter)])
                if not tenant:
                  tenant = self.env['tenant.partner'].create({
                                            'name': renter,
                                            'email': str(prop_id.id)+"@gmail.com",
                                          })

                year, month, day, hour, minute, second = xlrd.xldate_as_tuple(date,wb.datemode)
                date = datetime.datetime(year, month, day)
                year, month, day, hour, minute, second = xlrd.xldate_as_tuple(start_date,wb.datemode)
                start_date = datetime.datetime(year, month, day)
                year, month, day, hour, minute, second = xlrd.xldate_as_tuple(end_date,wb.datemode)
                end_date = datetime.datetime(year, month, day)

                tenancy_val = {
                                'name': "rent"+str(prop) ,
                                'building_id': building_id.id or False,
                                'property_id': prop_id.id,
                                'tenant_id': tenant.id,
                                'rent': rent,
                                'discount': discount,
                                'open_balance': balance,
                                'ten_date': date,
                                'date_start': date,
                                'date': end_date,
                                'sched': 'chosen_date',
                                'sched_date': start_date,
                                'rent_type_id': rent_type.id,
                                'discount_type': 'fixed',

                }


                tenancy_id = self.env['account.analytic.account'].create(tenancy_val)

        return {'type': 'ir.actions.act_window_close'}


