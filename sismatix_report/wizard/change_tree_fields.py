from odoo import api, fields, models, _, exceptions
from odoo import http
from urlparse import urlparse, parse_qs
import json



class ChangeTreeFields(models.Model):
	_name = "change.tree.fields"

	
	@api.depends('model')
	def _get_fields_domain(self):
		model = self.env.context.get('default_model')
		current_model = self.env['ir.model'].search([('model', '=', model)])
		current_fields = self.env.context.get('default_current_fields')
		return [('model_id', '=', current_model.id), ('name', 'not in', current_fields)]

	def _get_fav_view_domain(self):
		view_id = self.env.context.get('default_view_id')
		return [('view_id', '=', view_id), ('user_id', '=', self.env.user.id)]

	
	model = fields.Char('Model', default="none")
	def_fields = fields.Char('Default Fields')
	change_by = fields.Selection([('add', 'Add Fields To Current View'), ('choose', 'Choose From Favorite Views')],
								string="Change View By", default='add')
	fav_view = fields.Many2one('favorite.view', string="Favorite View", domain=_get_fav_view_domain)
	save_view = fields.Boolean('Save View ?')
	view_name = fields.Char('View Name')
	current_fields = fields.Char('Current Fields')
	fields = fields.Many2many('ir.model.fields', string="Fields", domain=_get_fields_domain)





	@api.onchange('fields')
	def change_view(self):
		if self.env.user.has_group('sismatix_report.group_can_change'):
			
			view_id = self.env.context.get('default_view_id')

			current_view = self.env['ir.ui.view'].search([('id', '=', view_id)])

			copy_view_res = self.env['copy.view'].search([('view_id', '=', current_view.id)])
			
			if not copy_view_res:
				copy_view = {}
				copy_view['view_id'] = current_view.id
				copy_view['field_parent'] = current_view.field_parent
				copy_view['inherit_id'] = current_view.inherit_id.id
				copy_view['model_data_id'] = current_view.model_data_id.id
				copy_view['priority'] = current_view.priority
				copy_view['type'] = current_view.type
				copy_view['arch_db'] = current_view.arch_db
				copy_view['key'] = current_view.key
				copy_view['active'] = current_view.active
				copy_view['arch_fs'] = current_view.arch_fs
				copy_view['name'] = current_view.name
				copy_view['mode'] = current_view.mode
				copy_view['model'] = current_view.model
				copy_view['m_state'] = current_view.m_state
				self.env['copy.view'].create(copy_view)

			if self.change_by == 'add':

				fields = ""
				
				for key in self.env.context.get('default_def_fields'):
					field_str = "<field name='"+key+"'/>"
					fields += field_str

				for field in self.fields:
					field_str = "<field name='"+field.name+"'/>"
					fields += field_str
				
				arch_db = "<?xml version='1.0'?><tree>"+fields+"</tree>"
				
				current_view.write({'arch_db': arch_db, 'm_state': 'modified'})

				if self.save_view == True:
					view_exists = self.env['favorite.view'].search([('name', '=', self.view_name)])
					if view_exists:
						raise exceptions.ValidationError("This View Name already Exists !!")
					else:
						self.env['favorite.view'].create({
							'name': self.view_name,
							'user_id': self.env.user.id,
							'view_id': view_id,
							'arch_db': arch_db,
							})

			elif self.change_by == 'choose':
				if self.fav_view:
					current_view.write({'arch_db': self.fav_view.arch_db, 'm_state': 'modified'})
				else:
					raise exceptions.ValidationError("Please Choose View From Favorite Views OR Add Fields To Current View ....")					
		else:
			raise exceptions.ValidationError("Sorry \n You didn't Have permission to Change this view ...")

		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}


	@api.model
	def return_view(self):
		views_modified = self.env['ir.ui.view'].search([('m_state', '=', 'modified')])

		if views_modified:
			for view in views_modified:
				copy_view = self.env['copy.view'].search([('view_id', '=', view.id)])
				view.write({
					'arch_db': copy_view.arch_db,
					'm_state': copy_view.m_state
					})

	
	def return_default(self):
		view_id = self.env.context.get('default_view_id')
		current_view_modified = self.env['ir.ui.view'].search([('id', '=', view_id), ('m_state', '=', 'modified')])

		if current_view_modified:
			copy_view = self.env['copy.view'].search([('view_id', '=', current_view_modified.id)])
			current_view_modified.write({
				'arch_db': copy_view.arch_db,
				'm_state': copy_view.m_state,
				})
		else:
			raise exceptions.ValidationError("Current View is The Default View !!! ")

		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}
