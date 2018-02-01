# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields


class operational_costs_report(models.Model):
	_name = "operational.costs.report"
	_auto = False

	active = fields.Boolean('Active')
	parent_id = fields.Many2one('account.asset.asset', 'Parent Property')
	type_id = fields.Many2one('property.type', 'Property Type')
	date = fields.Date('Purchase Date')
	operational_costs = fields.Float("Operational costs(%)")
	name = fields.Char('Asset Name')

	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		obj = self._cr.execute("""CREATE or REPLACE VIEW operational_costs_report as SELECT id,name,active,parent_id,type_id,operational_costs,date
			FROM account_asset_asset""" )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
