# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    payment_approver_id = fields.Many2one(
                            'hr.employee',
                            string='Payment Approver')
