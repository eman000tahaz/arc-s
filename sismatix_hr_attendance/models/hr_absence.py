# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrAbsence(models.Model):
	_name = "hr.absence"

	name = fields.Char('Name')
	times_ids = fields.One2many('absence.time', 'absence_id', string="Absence Times")


class AbsenceTime(models.Model):
	_name = "absence.time"

	name = fields.Char('Name')
	times = fields.Selection([
						('1', '1'),
						('2', '2'),
						('3', '3'),
						('4', '4'),
						('5', '5'),
						('6', '6'),
						('7', '7'),
						('8', '8'),
						('9', '9'),
						('10', '10'),], string="Times")
	rate = fields.Float('Rate')
	absence_id = fields.Many2one('hr.absence')