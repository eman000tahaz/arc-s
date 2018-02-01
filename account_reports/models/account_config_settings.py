from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    days_between_two_followups = fields.Integer(related='company_id.days_between_two_followups', string='Number of days between two follow-ups *')
