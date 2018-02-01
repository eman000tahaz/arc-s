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

{
    'name': 'Laxicon Mass payment to Vendor',
    'version': '1.0',
    'author': 'Laxicon Solution',
    'website': 'http://laxicon.in',
    'category': 'payment',
    'summary': 'Mass Payment',
    'description': '''user can pay at one time or receive payment with diffrent invoice.
''',
    'depends': ['account_payment_job', 'payment', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/mass_payment_data.xml',
        'wizard/account_general_ledger_wizz.xml',
        # 'wizard/check_report_wizard_view.xml',
        # 'report/accounr_general_ledger.xml',
        'report/mass_payment_report.xml',
        'views/account_payment.xml',
        'views/res_config_view.xml',
        'views/account_journal_view.xml',
        'views/partner_view.xml',
        'views/report_mass_payment.xml',
        'views/report_payment_transfer.xml',
        'views/report_check_book.xml',
    ],
    'active': True,
    'installable': True,
}
