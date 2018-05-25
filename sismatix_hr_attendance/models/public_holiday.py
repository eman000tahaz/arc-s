# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PublicHoliday(models.Model):
	_name = "public.holiday"

	reason = fields.Text('Reason')
	note = fields.Text('Notes')
	date_from = fields.Date()
	date_to = fields.Date()