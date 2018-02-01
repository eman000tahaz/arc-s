
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        # DO NOT FORWARDPORT! ONLY FOR v10!
        # Clean-up existing reports when the company configuration has changed for the user
        if 'company_id' in vals or 'company_ids' in vals:
            self.env['account.report.multicompany.manager'].sudo().search([('create_uid', 'in', self.ids)]).unlink()
        return res
