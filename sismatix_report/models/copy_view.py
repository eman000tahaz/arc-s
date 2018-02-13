from odoo import api, fields, models, _
 
class CopyView(models.Model):
	_name = "copy.view"

	field_parent = fields.Char()
	inherit_id = fields.Many2one('ir.ui.view')
	model_data_id = fields.Many2one('ir.model.data')
	priority = fields.Integer()
	type = fields.Char()
	arch_db = fields.Text()
	key = fields.Char()
	active = fields.Boolean()
	arch_fs = fields.Char()
	name = fields.Char()
	mode = fields.Char()
	model = fields.Char()
	m_state = fields.Char(default="default")
	view_id = fields.Integer()