# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields


class gfa_analysis_report(models.Model):
	_name = "gfa.analysis.report"
	_auto = False

	name = fields.Char('Property Name')
	active = fields.Boolean('Active')
	parent_id = fields.Many2one('account.asset.asset', 'Parent Property')
	type_id = fields.Many2one('property.type', 'Property Type')
	gfa_feet = fields.Float('GFA(Sqft)')
	date = fields.Date('Purchase Date')

	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		obj = self._cr.execute("""CREATE or REPLACE VIEW gfa_analysis_report as SELECT id,name,active,parent_id,type_id,gfa_feet,date
			FROM account_asset_asset """ )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
