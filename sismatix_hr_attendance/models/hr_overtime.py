# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrOvertime(models.Model):
	_name = "hr.overtime"

	name = fields.Char('Name')
	type_id = fields.Selection([('w-day', 'Working Day'), ('ph', 'Public Holiday'), ('w-end', 'Weekend')], string="Type")
	apply_after = fields.Float('Apply After')
	rate = fields.Float('Rate')


# class Daytype(models.Model):
# 	_name = "hr.day.type"

# 	name = fields.Char('Name')