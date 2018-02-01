# -*- encoding: utf-8 -*-

import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http, tools
from odoo.http import request
from odoo import SUPERUSER_ID

class Home(http.Controller):
	@http.route('/web/graph_data', type='json', auth="public")
	def graph_data(self, redirect=None, **kw):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		property_obj = pool['account.asset.asset'];
		proprty_ids = property_obj.search(cr,uid, []);
		duplicate_id = [];
		res = [{'name':'simulation','data':[]},{'name':'revenue','data':[]}];
		category = []
		for proprty in property_obj.browse(cr, uid, proprty_ids, context = context) :
			category.append(proprty.name)
			res[0]['data'].append([proprty.name,proprty.simulation]);
			res[1]['data'].append([proprty.name,proprty.revenue]);
		return [res,category]

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4: