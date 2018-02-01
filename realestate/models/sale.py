# -*- coding: utf-8 -*-

from odoo import models, fields

class sale_order_line(models.Model):
	_inherit = "sale.order.line"

	property_id = fields.Many2one('account.asset.asset', 'Property') 
	is_property =fields.Boolean('Is Property')

class sale_order(models.Model):
	_inherit = "sale.order"

	is_property = fields.Boolean('Is Property', default=False)
