# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrLate(models.Model):
	_name = "hr.late"

	name = fields.Char('Name')
	period_ids = fields.One2many('late.period', 'late_id', string="Late In Periods")

class LatePeriod(models.Model):
	_name = "late.period"

	time = fields.Float('Time')
	calc_type = fields.Selection([('fixed', 'Fixed'), ('rate', 'Rate')], string="Type")
	rate = fields.Float('Rate')
	amount = fields.Float('Amount')
	late_id = fields.Many2one('hr.late')