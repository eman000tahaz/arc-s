# -*- coding: utf-8 -*-

import odoo.tools
import datetime
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class partner_wizard_spam(models.TransientModel):
	""" Mass Mailing """

	_name = "tenant.wizard.mail"
	_description = "Mass Mailing"

	@api.multi
	def mass_mail_send(self):
		partner_pool = self.env['tenancy.rent.schedule']
		active_ids = partner_pool.search([('start_date' , '<', datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))])
		partners = partner_pool.browse(active_ids.ids)
		for partner in partners:
				if partner.rel_tenant_id.parent_id:
					if partner.rel_tenant_id.parent_id[0].email:
						to = '"%s" <%s>' % (partner.rel_tenant_id.name, partner.rel_tenant_id.parent_id[0].email)
		#TODO: add some tests to check for invalid email addresses
		#CHECKME: maybe we should use res.partner/email_send
						tools.email_send(tools.config.get('email_from', False),
										 [to],
										 'Reminder for rent payment',
										 '''
										 Hello Mr %s,\n
										 Your rent QAR %d of %s is unpaid so kindly pay as soon as possible.
										 \n
										 Regards,
										 Administrator.
										 Property management firm.
										 ''' %(partner.rel_tenant_id.name, partner.amount,partner.start_date))
		return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
		