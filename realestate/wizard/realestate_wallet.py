# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class RealestateWalletReport(models.TransientModel):
    _name = "realestate.wallet.report"

    wallet_id = fields.Many2one('realestate.wallet', string='Portfolio')

    @api.multi
    def open_wallet_tree(self):
        for data1 in self:
            data = data1.read([])[0]
            wallet_id = data['wallet_id']
            wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'wallet_tree_view')[1]
            wallet_ids = self.env['realestate.wallet'].search([('id','=',wallet_id[0])])
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'tree',
            'res_model': 'realestate.wallet',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context':self._context,
            'domain':[('id','in',wallet_ids.ids)],
            }    


    @api.multi
    def print_report(self, data):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['wallet_id'])[0]
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'realestate.report_realestate_wallet', data=data)