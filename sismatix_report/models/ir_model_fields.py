from odoo import api, fields, models, _

class IrModelFieldsLine(models.Model):
	_name = "ir.model.fields.line"
	
	sequance = fields.Integer('Sequance', default=20, store=False)
	field = fields.Many2many('ir.model.fields', string="Field")

		 
class IrModelFields(models.Model):
	_inherit = "ir.model.fields"

	sequance = fields.Integer('Sequance', default=20, store=False)

	# @api.multi
	# def write(self, vals):
	# 	# For the moment renaming a sparse field or changing the storing system
	# 	# is not allowed. This may be done later
	# 	if 'serialization_field_id' in vals or 'name' in vals:
	# 		for field in self:
	# 			if 'serialization_field_id' in vals and field.serialization_field_id.id != vals['serialization_field_id']:
	# 				raise UserError(_('Changing the storing system for field "%s" is not allowed.') % field.name)
	# 			if field.serialization_field_id and (field.name != vals['name']):
	# 				raise UserError(_('Renaming sparse field "%s" is not allowed') % field.name)

	# 	# if set, *one* column can be renamed here
	# 	column_rename = None

	# 	# names of the models to patch
	# 	patched_models = set()

	# 	if vals and self:
	# 		# check selection if given
	# 		if vals.get('selection'):
	# 			self._check_selection(vals['selection'])

	# 		for item in self:
 #                # if item.state != 'manual':
 #                #     raise UserError(_('Properties of base fields cannot be altered in this manner! '
 #                #                       'Please modify them through Python code, '
 #                #                       'preferably through a custom addon!'))

	# 			if vals.get('model_id', item.model_id.id) != item.model_id.id:
	# 				raise UserError(_("Changing the model of a field is forbidden!"))

	# 			if vals.get('ttype', item.ttype) != item.ttype:
	# 				raise UserError(_("Changing the type of a field is not yet supported. "
	# 								"Please drop it and create it again!"))

	# 			obj = self.pool.get(item.model)
	# 			field = getattr(obj, '_fields', {}).get(item.name)

	# 			if vals.get('name', item.name) != item.name:
	# 				# We need to rename the column
	# 				item._prepare_update()
	# 				if column_rename:
	# 					raise UserError(_('Can only rename one field at a time!'))
	# 				column_rename = (obj._table, item.name, vals['name'], item.index)

	# 			# We don't check the 'state', because it might come from the context
	# 			# (thus be set for multiple fields) and will be ignored anyway.
	# 			if obj is not None and field is not None:
	# 				patched_models.add(obj._name)

	# 	# These shall never be written (modified)
	# 	for column_name in ('model_id', 'model', 'state'):
	# 		if column_name in vals:
	# 			del vals[column_name]

	# 	res = super(IrModelFields, self).write(vals)

	# 	self.pool.clear_manual_fields()

	# 	if column_rename:
	# 		# rename column in database, and its corresponding index if present
	# 		table, oldname, newname, index = column_rename
	# 		self._cr.execute('ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % (table, oldname, newname))
	# 		if index:
	# 			self._cr.execute('ALTER INDEX "%s_%s_index" RENAME TO "%s_%s_index"' % (table, oldname, table, newname))

	# 	if column_rename or patched_models:
	# 		# setup models, this will reload all manual fields in registry
	# 		self.pool.setup_models(self._cr, partial=(not self.pool.ready))

	# 	if patched_models:
	# 		# update the database schema of the models to patch
	# 		models = self.pool.descendants(patched_models, '_inherits')
	# 		self.pool.init_models(self._cr, models, dict(self._context, update_custom_fields=True))

	# 	if column_rename or patched_models:
	# 		self.pool.signal_registry_change()

	# 	return res