# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models
import datetime


class tenancy_final_detail_ar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(tenancy_final_detail_ar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'get_current_month_deserved': self.get_current_month_deserved,
                                  'get_insurance_details': self.get_insurance_details,
                                  'get_maintenance_details': self.get_maintenance_details,
                                  'get_new_contract_details': self.get_new_contract_details,
                                  'get_new_contract_next_months': self.get_new_contract_next_months,
                                  'get_new_contract_deserved': self.get_new_contract_deserved,
                                  'get_current_delay': self.get_current_delay,
                                  'get_legal_cases': self.get_legal_cases,
                                  'get_total': self.get_total,
                                  'get_insurance_total': self.get_insurance_total,
                                  'get_total_new_contract': self.get_total_new_contract,
                                  'get_total_new_contract_deserved': self.get_total_new_contract_deserved,
                                  'get_total_new_contract_next_months': self.get_total_new_contract_next_months,
                                  'get_total_current_delay': self.get_total_current_delay,
                                  'get_total_legal_cases': self.get_total_legal_cases,
                                  'get_profit_loss_account': self.get_profit_loss_account,
                                  'get_cash_flow_statement': self.get_cash_flow_statement,
                                  'get_balance_sheet': self.get_balance_sheet,
                                  })
        self.balance_sheet = {}
        self.balance_sheet['cash'] = 0
        self.balance_sheet['advance_payment_for_property_manager'] = 0
        self.balance_sheet['new_contract_advance_payment_management_fees'] = 0
        self.balance_sheet['uncollected_income'] = 0
        self.balance_sheet['total_asset'] = 0

        self.balance_sheet['realestate_fees_for_uncollected_income'] = 0
        self.balance_sheet['unaccrued_income'] = 0
        self.balance_sheet['insurance_tenants'] = 0
        self.balance_sheet['total_liabilities'] = 0
        self.balance_sheet['accumlative_net_income'] = 0

        self.cash_flow_statement = {}
        self.cash_flow_statement['net_income'] = 0
        self.cash_flow_statement['uncollected_income'] = 0
        self.cash_flow_statement['unpaid_realestate_fees'] = 0
        self.cash_flow_statement['collected_income'] = 0
        self.cash_flow_statement['paid_realestate_fees'] = 0
        self.cash_flow_statement['unaccrued_income'] = 0
        self.cash_flow_statement['advance_payment_realestate_fees'] = 0
        self.cash_flow_statement['accrued_income'] = 0
        self.cash_flow_statement['accrued_rental_brokerage_fees'] = 0
        self.cash_flow_statement['accrued_rental_brokerage_fees2'] = 0
        self.cash_flow_statement['advance_payment_rental_brokerage_fees'] = 0
        self.cash_flow_statement['paid_insurance_tenants'] = 0
        self.cash_flow_statement['insurance_tenants'] = 0
        self.cash_flow_statement['net_cash_flow_statement'] = 0

        self.profit_loss_account = {}
        self.profit_loss_account['rental_income_current'] = 0
        self.profit_loss_account['realestate_fees_current'] = 0
        self.profit_loss_account['expenses_current'] = 0
        self.profit_loss_account['other_revenue_current'] = 0
        self.profit_loss_account['rental_brokerage_fees_current'] = 0
        self.profit_loss_account['net_income_current'] = 0
        self.profit_loss_account['rental_income_year'] = 0
        self.profit_loss_account['realestate_fees_year'] = 0
        self.profit_loss_account['expenses_year'] = 0
        self.profit_loss_account['other_revenue_year'] = 0
        self.profit_loss_account['rental_brokerage_fees_year'] = 0
        self.profit_loss_account['net_income_year'] = 0

        self.total_new_contract = {}
        self.total_new_contract['total_rent'] = 0
        self.total_new_contract['total_comession'] = 0

        self.total_new_contract_deserved = {}
        self.total_new_contract_deserved['total_rent'] = 0
        self.total_new_contract_deserved['total_comession'] = 0

        self.total_new_contract_next_months = {}
        self.total_new_contract_next_months['total_rent'] = 0
        self.total_new_contract_next_months['total_comession'] = 0

        self.total_current_delay = {}
        self.total_current_delay['total_rent'] = 0
        self.total_current_delay['total_comession'] = 0

        self.total_legal_cases = {}
        self.total_legal_cases['total_rec_current_month'] = 0
        self.total_legal_cases['total_rec_to_this_month'] = 0
        self.total_legal_cases['total_deserved_amount'] = 0

        self.total_insurance = {}
        self.total_insurance['total_insurnace'] = 0
        self.total_insurance['total_convert_to_rent'] = 0
        self.total_insurance['total_insurance_returned'] = 0
        self.total_insurance['total_other_income'] = 0
        self.total_insurance['total_new_insurance'] = 0
        self.total_insurance['total_insurance_balance'] = 0

        self.total_res = {}
        self.total_res['basic_rent'] = 0
        self.total_res['unoccupied'] = 0
        self.total_res['insurance'] = 0
        self.total_res['total_maintenance'] = 0
        self.total_res['Total'] = 0
        self.total_res['current_reserve_rent'] = 0
        self.total_res['months_before_reserve_rent'] = 0
        self.total_res['years_before_reserve_rent'] = 0
        self.total_res['Advance_Balance'] = 0
        self.total_res['current_paid_rent'] = 0
        self.total_res['months_before_paid_rent'] = 0
        self.total_res['advance_paid_rent'] = 0
        self.total_res['from_advance_paid_rent'] = 0
        self.total_res['other_income'] = 0
        self.total_res['delay_on_pay'] = 0
        self.total_res['delay_on_current_pay'] = 0
        self.total_res['unoccupied'] = 0
        self.total_res['insurance'] = 0
        self.total_res['Total'] = 0
        self.context = context

    def get_current_month_deserved(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        selectedyear = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            res = {}
            res['property_name'] = property_id_new.name
            res['tenant'] = 'NONE'
            res['basic_rent'] = property_id_new.ground_rent
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id)])
            if tenancy_ids:
                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    res['tenant'] = tenancy_id.tenant_id.name
                    res['basic_rent'] = tenancy_id.rent
                    res['current_reserve_rent'] = 0
                    res['months_before_reserve_rent'] = 0
                    res['years_before_reserve_rent'] = 0
                    res['Advance_Balance'] = 0
                    res['current_paid_rent'] = 0
                    res['months_before_paid_rent'] = 0
                    res['advance_paid_rent'] = 0
                    res['from_advance_paid_rent'] = 0
                    res['other_income'] = 0
                    res['delay_on_pay'] = 0
                    res['delay_on_current_pay'] = 0
                    res['unoccupied'] = 0
                    res['insurance'] = tenancy_id.deposit
                    res['Total'] = 0
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            if rent.move_check and rent.start_date >= start_date and rent.end_date <= end_date:
                                res['current_reserve_rent'] = rent.amount
                            rentyear = datetime.datetime.strptime(rent.start_date, "%Y-%m-%d").strftime("%Y")
                            if not rent.paid_check and rent.move_check and rentyear < selectedyear:
                                res['years_before_reserve_rent'] += rent.amount
                            if not rent.paid_check and rent.move_check and rent.start_date <= start_date and rentyear == selectedyear:
                                res['months_before_reserve_rent'] += rent.amount
                            if rent.paid_check and rent.start_date >= start_date and rent.paid_id.payment_date < start_date:
                                res['Advance_Balance'] += rent.amount
                            if rent.paid_check and rent.move_check and rent.start_date >= start_date and rent.end_date <= end_date and rent.paid_id.payment_date >= start_date and rent.paid_id.payment_date <= end_date:
                                res['current_paid_rent'] += rent.amount
                            if rent.paid_check and rent.move_check and rent.start_date < start_date and rent.paid_id.payment_date >= start_date and rent.paid_id.payment_date <= end_date:
                                res['months_before_paid_rent'] += rent.amount
                            if rent.paid_check and not rent.move_check and rent.start_date > start_date and rent.paid_id.payment_date > start_date and rent.paid_id.payment_date < end_date:
                                res['advance_paid_rent'] += rent.amount
                            if rent.paid_check and rent.move_check and rent.start_date >= start_date and rent.end_date <= end_date and rent.paid_id.payment_date < start_date:
                                res['from_advance_paid_rent'] += rent.amount
                            if not rent.paid_check and rent.move_check and rent.start_date >= start_date and rent.start_date <= end_date:
                                res['delay_on_current_pay'] = rent.amount
                                res['delay_on_pay'] += rent.amount
                            if not rent.paid_check and rent.move_check and rent.start_date < start_date:
                                res['delay_on_pay'] += rent.amount
                        res['Total'] = res['current_paid_rent'] + res['months_before_paid_rent'] + res[
                            'advance_paid_rent'] + res['insurance']

            else:
                res['current_reserve_rent'] = 0
                res['months_before_reserve_rent'] = 0
                res['years_before_reserve_rent'] = 0
                res['Advance_Balance'] = 0
                res['current_paid_rent'] = 0
                res['months_before_paid_rent'] = 0
                res['advance_paid_rent'] = 0
                res['from_advance_paid_rent'] = 0
                res['other_income'] = 0
                res['delay_on_pay'] = 0
                res['delay_on_current_pay'] = 0
                res['unoccupied'] = property_id_new.ground_rent
                res['insurance'] = 0
                res['Total'] = 0
            self.total_res['current_reserve_rent'] += res['current_reserve_rent']
            self.profit_loss_account['rental_income_current'] += res['current_reserve_rent']
            self.profit_loss_account['realestate_fees_current'] -= res['current_reserve_rent'] * 0.03
            self.total_res['months_before_reserve_rent'] += res['months_before_reserve_rent']
            self.total_res['years_before_reserve_rent'] += res['years_before_reserve_rent']
            self.total_res['Advance_Balance'] += res['Advance_Balance']
            self.total_res['current_paid_rent'] += res['current_paid_rent']
            self.total_res['months_before_paid_rent'] += res['months_before_paid_rent']
            self.total_res['advance_paid_rent'] += res['advance_paid_rent']
            self.total_res['from_advance_paid_rent'] += res['from_advance_paid_rent']
            self.total_res['other_income'] += res['other_income']
            self.total_res['delay_on_pay'] += res['delay_on_pay']
            self.total_res['delay_on_current_pay'] += res['delay_on_current_pay']
            self.total_res['unoccupied'] += res['unoccupied']
            self.total_res['insurance'] += res['insurance']
            self.total_res['Total'] += res['Total']
            result.append(res)
        return result

    def get_maintenance_details(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        # selectedyear =  datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            property_maintenance_obj = self.pool.get("property.maintenance")
            property_maintenance_ids = property_maintenance_obj.search(self.cr, self.uid,
                                                                       [('property_id', '=', property_id_new.id),
                                                                        ('date', '>=', start_date),
                                                                        ('date', '<=', end_date)])
            if property_maintenance_ids:
                for property_maintenance_id in property_maintenance_obj.browse(self.cr, self.uid,
                                                                               property_maintenance_ids):
                    res = {}
                    res['property_name'] = property_id_new.name
                    res['type'] = property_maintenance_id.type.name
                    res['cost'] = property_maintenance_id.cost
                    res['notes'] = property_maintenance_id.notes
                    self.total_res['total_maintenance'] += res['cost']
                    self.profit_loss_account['expenses_current'] += res['cost']
                    result.append(res)

        return result

    def get_insurance_details(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        selectedyear = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id)])
            if tenancy_ids:
                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    res = {}
                    res['property_name'] = property_id_new.name
                    res['tenant'] = tenancy_id.tenant_id.name
                    res['nationality'] = tenancy_id.tenant_id.country_id.name
                    res['start_date'] = tenancy_id.date_start
                    res['insurance'] = tenancy_id.deposit
                    res['convert_to_rent'] = 0
                    res['insurance_returned'] = 0
                    res['other_income'] = 0
                    res['new_insurance'] = 0
                    res['insurance_balance'] = 0
                    if tenancy_id.deposit_return and tenancy_id.acc_pay_dep_ret_id.payment_date >= start_date and tenancy_id.acc_pay_dep_ret_id.payment_date <= end_date:
                        res['insurance_returned'] = -1 * tenancy_id.acc_pay_dep_ret_id.amount
                    if tenancy_id.deposit_received and tenancy_id.acc_pay_dep_rec_id.payment_date >= start_date and tenancy_id.acc_pay_dep_rec_id.payment_date <= end_date:
                        res['new_insurance'] = tenancy_id.acc_pay_dep_rec_id.amount
                        res['insurance'] = 0
                    res['insurance_balance'] = res['new_insurance'] + res['insurance'] + res['insurance_returned']

                    self.total_insurance['total_insurnace'] += res['new_insurance']
                    self.total_insurance['total_convert_to_rent'] += res['convert_to_rent']
                    self.total_insurance['total_insurance_returned'] += res['insurance_returned']
                    self.total_insurance['total_other_income'] += res['other_income']
                    self.profit_loss_account['other_revenue_current'] += res['other_income']
                    self.total_insurance['total_new_insurance'] += res['new_insurance']
                    self.total_insurance['total_insurance_balance'] += res['insurance_balance']
                    result.append(res)
        return result

    def get_new_contract_details(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        selectedyear = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id),
                                                                 ('date_start', '>=', start_date),
                                                                 ('date_start', '<=', end_date)])

            if tenancy_ids:
                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            res = {}
                            if rent.paid_check and rent.start_date >= start_date and rent.end_date <= end_date and \
                                            rent.paid_id.payment_date >= start_date and rent.paid_id.payment_date <= end_date:
                                res['property_name'] = property_id_new.name
                                res['tenant'] = tenancy_id.tenant_id.name
                                res['rent'] = rent.amount
                                res['comession'] = 0.5 * rent.amount
                                self.total_new_contract['total_rent'] += rent.amount
                                self.total_new_contract['total_comession'] += rent.amount * 0.5
                                result.append(res)
        return result

    def get_new_contract_next_months(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        selectedyear = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id),
                                                                 ('date_start', '>=', start_date),
                                                                 ('date_start', '<=', end_date)])

            if tenancy_ids:
                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            res = {}
                            if rent.paid_check and rent.start_date >= start_date and rent.end_date <= end_date and \
                                            rent.paid_id.payment_date < start_date:
                                res['property_name'] = property_id_new.name
                                res['tenant'] = tenancy_id.tenant_id.name
                                res['rent'] = rent.amount
                                res['comession'] = 0.5 * rent.amount
                                self.total_new_contract_next_months['total_rent'] += rent.amount
                                self.profit_loss_account['rental_brokerage_fees_current'] += rent.amount * 0.5
                                self.total_new_contract_next_months['total_comession'] += rent.amount * 0.5
                                result.append(res)
        return result

    def get_new_contract_deserved(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id),
                                                                 ('date_start', '>=', start_date),
                                                                 ('date_start', '<=', end_date)])

            if tenancy_ids:
                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            res = {}
                            if rent.move_check and not rent.paid_check and rent.start_date >= start_date and rent.end_date <= end_date:
                                res['property_name'] = property_id_new.name
                                res['tenant'] = tenancy_id.tenant_id.name
                                res['rent'] = rent.amount
                                res['comession'] = 0.5 * rent.amount
                                self.total_new_contract_deserved['total_rent'] += rent.amount
                                self.total_new_contract_deserved['total_comession'] += rent.amount * 0.5
                                result.append(res)
        return result

    def get_current_delay(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id),
                                                                 ('date_start', '<=', start_date)])

            if tenancy_ids:

                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    res = {}
                    rent_count = 0
                    rent_amount = 0
                    commision = 0
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            if rent.move_check and not rent.paid_check and rent.start_date <= start_date and rent.start_date <= end_date:
                                res['property_name'] = property_id_new.name
                                res['tenant'] = tenancy_id.tenant_id.name
                                rent_count += 1
                                rent_amount += rent.amount
                                commision += rent.amount * 0.03
                                res['no_months'] = rent_count
                                res['rent'] = rent_amount
                                res['comession'] = commision
                                result.append(res)

                    self.total_current_delay['total_rent'] += rent_amount
                    self.total_current_delay['total_comession'] += commision

        return result

    def get_legal_cases(self, start_date, end_date, property_id):
        result = []
        property_obj = self.pool.get("account.asset.asset")
        propert_ids = property_obj.search(self.cr, self.uid, [('parent_id', '=', property_id[0])])
        for property_id_new in property_obj.browse(self.cr, self.uid, propert_ids):
            self.total_res['basic_rent'] += property_id_new.ground_rent
            tenancy_obj = self.pool.get("account.analytic.account")
            tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id', '=', property_id_new.id),
                                                                 ('date_start', '<=', start_date)])

            if tenancy_ids:

                for tenancy_id in tenancy_obj.browse(self.cr, self.uid, tenancy_ids):
                    res = {}
                    rent_count = 0
                    rent_amount = 0
                    commision = 0
                    tenancy_rent_schedule_obj = self.pool.get("tenancy.rent.schedule")
                    tenancy_rent_schedule_ids = tenancy_rent_schedule_obj.search(self.cr, self.uid,
                                                                                 [('tenancy_id', '=', tenancy_id.id)])
                    res['rec_current_month'] = 0
                    res['rec_to_this_month'] = 0
                    res['deserved_amount'] = 0
                    if tenancy_rent_schedule_ids:
                        for rent in tenancy_rent_schedule_obj.browse(self.cr, self.uid, tenancy_rent_schedule_ids):
                            if rent.case_id:
                                res['property_name'] = property_id_new.name
                                res['tenant'] = tenancy_id.tenant_id.name
                                rent_amount += rent.amount
                                if rent.paid_check and rent.paid_id.payment_date >= start_date and rent.paid_id.payment_date <= end_date:
                                    res['rec_current_month'] += rent.paid_id.amount
                                if rent.paid_check and rent.paid_id.payment_date <= end_date:
                                    res['rec_to_this_month'] += rent.paid_id.amount
                                if rent.move_check and not rent.paid_check and rent.start_date <= end_date and rent.start_date >= start_date:
                                    res['deserved_amount'] += rent.amount
                                    rent_count += 1
                                res['no_months'] = rent_count
                                res['case_type'] = rent.case_id.type_id.name
                                result.append(res)
                    self.total_legal_cases['total_rec_current_month'] += res['rec_current_month']
                    self.total_legal_cases['total_rec_to_this_month'] += res['rec_to_this_month']
                    self.total_legal_cases['total_deserved_amount'] += res['deserved_amount']
        return result

    def get_total(self):
        return self.total_res

    def get_insurance_total(self):
        return self.total_insurance

    def get_total_new_contract(self):
        return self.total_new_contract

    def get_total_new_contract_deserved(self):
        return self.total_new_contract_deserved

    def get_total_new_contract_next_months(self):
        return self.total_new_contract_next_months

    def get_total_current_delay(self):
        return self.total_current_delay

    def get_total_legal_cases(self):
        return self.total_legal_cases

    def get_profit_loss_account(self):

        self.profit_loss_account['realestate_fees_current'] = self.profit_loss_account[
            'realestate_fees_current']
        self.profit_loss_account['expenses_current'] = -1 * self.profit_loss_account['expenses_current']
        # self.profit_loss_account['rental_brokerage_fees_current'] = -1 * self.profit_loss_account[
        #     'rental_brokerage_fees_current']

        self.profit_loss_account['rental_brokerage_fees_current'] = -1 * self.total_new_contract['total_comession']

        self.profit_loss_account['net_income_current'] = self.profit_loss_account['rental_income_current'] \
                                                         + self.profit_loss_account['realestate_fees_current'] \
                                                         + self.profit_loss_account['expenses_current'] \
                                                         + self.profit_loss_account['other_revenue_current'] \
                                                         + self.profit_loss_account['rental_brokerage_fees_current']

        self.profit_loss_account['realestate_fees_year'] = -1 * self.profit_loss_account[
            'realestate_fees_year']
        self.profit_loss_account['expenses_year'] = -1 * self.profit_loss_account['expenses_year']
        self.profit_loss_account['rental_brokerage_fees_year'] = -1 * self.profit_loss_account[
            'rental_brokerage_fees_year']

        self.profit_loss_account['net_income_year'] = self.profit_loss_account['rental_income_year'] \
                                                      + self.profit_loss_account['realestate_fees_year'] \
                                                      + self.profit_loss_account['expenses_year'] \
                                                      + self.profit_loss_account['other_revenue_year'] \
                                                      + self.profit_loss_account['rental_brokerage_fees_year']

        return self.profit_loss_account

    def get_cash_flow_statement(self):

        self.cash_flow_statement['net_income'] = self.profit_loss_account['net_income_current']
        self.cash_flow_statement['uncollected_income'] = self.total_res['delay_on_current_pay']
        self.cash_flow_statement['unpaid_realestate_fees'] = self.total_res['delay_on_current_pay'] * 0.03
        self.cash_flow_statement['collected_income'] = self.total_res['months_before_paid_rent']
        self.cash_flow_statement['paid_realestate_fees'] = self.total_res['months_before_paid_rent'] * 0.03
        self.cash_flow_statement['unaccrued_income'] = self.total_res['advance_paid_rent']
        self.cash_flow_statement['advance_payment_realestate_fees'] = self.total_res[
                                                                                   'advance_paid_rent'] * 0.03
        self.cash_flow_statement['accrued_income'] = self.total_res['from_advance_paid_rent']
        self.cash_flow_statement['accrued_rental_brokerage_fees'] = self.total_res['from_advance_paid_rent'] * 0.03
        self.cash_flow_statement['accrued_rental_brokerage_fees2'] = self.total_new_contract_next_months[
            'total_comession']
        self.cash_flow_statement['advance_payment_rental_brokerage_fees'] = self.total_new_contract_next_months[
            'total_comession']
        self.cash_flow_statement['paid_insurance_tenants'] = self.total_insurance['total_insurance_returned'] + \
                                                             self.total_insurance['total_other_income']
        self.cash_flow_statement['insurance_tenants'] = self.total_res['insurance']

        self.cash_flow_statement['uncollected_income'] = -1 * self.cash_flow_statement['uncollected_income']
        self.cash_flow_statement['paid_realestate_fees'] = -1 * self.cash_flow_statement[
            'paid_realestate_fees']
        self.cash_flow_statement['advance_payment_realestate_fees'] = -1 * self.cash_flow_statement[
            'advance_payment_realestate_fees']
        self.cash_flow_statement['accrued_income'] = -1 * self.cash_flow_statement['accrued_income']
        self.cash_flow_statement['advance_payment_rental_brokerage_fees'] = -1 * self.cash_flow_statement[
            'advance_payment_rental_brokerage_fees']
        self.cash_flow_statement['paid_insurance_tenants'] = -1 * self.cash_flow_statement[
            'advance_payment_rental_brokerage_fees']

        self.cash_flow_statement['net_cash_flow_statement'] = self.cash_flow_statement['net_income'] + \
                                                              self.cash_flow_statement['uncollected_income'] + \
                                                              self.cash_flow_statement[
                                                                  'unpaid_realestate_fees'] + \
                                                              self.cash_flow_statement['collected_income'] + \
                                                              self.cash_flow_statement[
                                                                  'paid_realestate_fees'] + \
                                                              self.cash_flow_statement['unaccrued_income'] + \
                                                              self.cash_flow_statement[
                                                                  'advance_payment_realestate_fees'] + \
                                                              self.cash_flow_statement['accrued_income'] + \
                                                              self.cash_flow_statement[
                                                                  'accrued_rental_brokerage_fees'] + \
                                                              self.cash_flow_statement[
                                                                  'accrued_rental_brokerage_fees2'] + \
                                                              self.cash_flow_statement[
                                                                  'advance_payment_rental_brokerage_fees'] + \
                                                              self.cash_flow_statement['paid_insurance_tenants'] + \
                                                              self.cash_flow_statement['insurance_tenants']

        return self.cash_flow_statement

    def get_balance_sheet(self):

        self.balance_sheet['cash'] = 0
        self.balance_sheet['advance_payment_for_property_manager'] = (
                                                                         self.total_res['Advance_Balance'] -
                                                                         self.total_res[
                                                                             'from_advance_paid_rent'] + self.total_res[
                                                                             'advance_paid_rent']) * 0.03
        self.balance_sheet['new_contract_advance_payment_management_fees'] = self.total_new_contract_next_months[
            'total_comession']

        self.balance_sheet['uncollected_income'] = self.total_res['delay_on_pay']
        self.balance_sheet['total_asset'] = self.balance_sheet['cash'] + self.balance_sheet[
            'advance_payment_for_property_manager'] + self.balance_sheet[
                                                'new_contract_advance_payment_management_fees'] + self.balance_sheet[
                                                'uncollected_income']
        self.balance_sheet['realestate_fees_for_uncollected_income'] = self.balance_sheet[
                                                                                    'uncollected_income'] * 0.03
        self.balance_sheet['unaccrued_income'] = self.total_res['Advance_Balance'] - self.total_res[
            'from_advance_paid_rent'] + self.total_res['advance_paid_rent']

        self.balance_sheet['insurance_tenants'] = self.total_insurance['total_insurance_balance']

        self.balance_sheet['total_liabilities'] = self.balance_sheet[
                                                      'realestate_fees_for_uncollected_income'] + \
                                                  self.balance_sheet['unaccrued_income'] + self.balance_sheet[
                                                      'insurance_tenants']
        self.balance_sheet['accumlative_net_income'] = self.balance_sheet['total_asset'] - self.balance_sheet[
            'total_liabilities']
        return self.balance_sheet


class report_tenancy_final_byprop(models.AbstractModel):
    _name = 'report.realestate.report_tenancy_final_by_property_ar'
    _inherit = 'report.abstract_report'
    _template = 'realestate.report_tenancy_final_by_property_ar'
    _wrapped_report_class = tenancy_final_detail_ar

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
