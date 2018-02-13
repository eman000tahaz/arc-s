from odoo import api, fields, models, _
 
class IrUiView(models.Model):
	_inherit = "ir.ui.view"

	m_state = fields.Char('State', default='default')