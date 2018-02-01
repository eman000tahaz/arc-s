# -*- coding: utf-8 -*-

import odoo.tools
import datetime
import urllib
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class tenant_sms_send(models.TransientModel):
	""" Create Menu """

	_name = "tenant.sms.send"
	_description = "Send SMS"

	user = fields.Char('Login', size=256,required=True)
	password = fields.Char('Password', size=256,required=True)

	@api.multi
	def sms_send(self):
		partner_pool = self.env['tenancy.rent.schedule']
		active_ids = partner_pool.search([('start_date' , '<', datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)), ('paid' , '=', False)])
		partners = partner_pool.browse(active_ids.ids)
		for partner in partners:
				if partner.rel_tenant_id.parent_id:
					if partner.rel_tenant_id.parent_id[0].mobile:
						for data in self:
# bulksms API is used for messege sending
							urllib.urlopen('''http://bulksms.vsms.net:5567/eapi/submission/send_sms/2/2.0?username=%s&password=%s&message=Hello Mr %s,\nYour rent QAR %d of %s is unpaid so kindly pay as soon as possible.\nRegards,\nProperty management firm.&msisdn=%s''' %(data.user,data.password,partner.rel_tenant_id.name, partner.amount,partner.start_date,partner.rel_tenant_id.parent_id[0].mobile))
		return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: