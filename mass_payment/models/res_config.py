# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    payment_approver_id = fields.Many2one(
                            'hr.employee',
                            related='company_id.payment_approver_id',
                            string='Payment Approver')
