# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrDiffTime(models.Model):
	_name = "hr.diff.time"

	name = fields.Char('Name')
	period_ids = fields.One2many('diff.period', 'diff_id', string="Difference Time Periods")

class LatePeriod(models.Model):
	_name = "diff.period"

	time = fields.Float('Time')
	calc_type = fields.Selection([('fixed', 'Fixed'), ('rate', 'Rate')], string="Type")
	rate = fields.Float('Rate')
	amount = fields.Float('Amount')
	diff_id = fields.Many2one('hr.diff.time')