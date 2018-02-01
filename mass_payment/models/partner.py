# -*- encoding: UTF-8 -*-

from openerp import fields, models


class res_partner(models.Model):
    _inherit = 'res.partner'

    bank = fields.Char('Bank Name')
    acc_number = fields.Char('Account Number')
    swift_code = fields.Char('Swift Code')
    iban_no = fields.Char('IBAN No')
