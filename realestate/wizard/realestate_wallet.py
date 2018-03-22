# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class RealestateWalletReport(models.TransientModel):
    _name = "realestate.wallet.report"

    wallet_id = fields.Many2one('realestate.wallet', string='Wallet')

    @api.multi
    def print_report(self, data):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['wallet_id'])[0]
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'realestate.report_realestate_wallet', data=data)