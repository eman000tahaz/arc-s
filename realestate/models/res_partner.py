# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _

class res_partner(models.Model):
	_inherit = "res.partner"

	tenant = fields.Boolean('Tenant', help="Check this box if this contact is a tenant.")
	occupation = fields.Char('Occupation', size=20)
	agent = fields.Boolean('Agent', help="Check this box if this contact is a Agent.")

class res_users(models.Model):
	_inherit = "res.users"

	tenant_id = fields.Many2one('tenant.partner','Related Tenant')
	tenant_ids = fields.Many2many('tenant.partner','rel_ten_user','user_id','tenant_id','All Tenents')
