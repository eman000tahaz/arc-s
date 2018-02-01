# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class crm_make_sale(models.TransientModel):
	""" Make sale  order for crm """

	_name = "crm.make.sale"
	_description = "Make sales"

	@api.model
	def _selectPartner(self):
		"""
		This function gets default value for partner_id field.
		@param self: The object pointer
		"""
		if self._context is None:
			self._context = {}
		active_id = self._context and self._context.get('active_id', False) or False
		if not active_id:
			return False
		lead_brw = self.env['crm.lead'].browse(active_id)
		lead = lead_brw.read(['partner_id'])[0]
		return lead['partner_id'][0] if lead['partner_id'] else False

	partner_id = fields.Many2one('res.partner', 'Customer', required=True,default=_selectPartner, domain=[('customer','=',True)])
	close = fields.Boolean('Mark Won',default=False, help='Check this to close the opportunity after having created the sales order.')


	@api.model
	def view_init(self, fields_list):
		return super(crm_make_sale, self).view_init(fields_list)

	@api.multi
	def makeOrder(self):
		"""
		This function  create Quotation on given case.
		@param self: The object pointer
		@return: Dictionary value of created sales order.
		"""
		context = dict(self._context or {})
		context.pop('default_state', False)
		data = context and context.get('active_ids', []) or []
		for make in self:
			partner = make.partner_id
			partner_addr = partner.address_get(['default', 'invoice', 'delivery', 'contact'])
			pricelist = partner.property_product_pricelist.id
			fpos = partner.property_account_position_id and partner.property_account_position_id.id or False
			payment_term = partner.property_payment_term_id and partner.property_payment_term_id.id or False
			new_ids = []
			for case in self.env['crm.lead'].browse(data):
				if not partner and case.partner_id:
					partner = case.partner_id
					fpos = partner.property_account_position_id and partner.property_account_position_id.id or False
					payment_term = partner.property_payment_term_id and partner.property_payment_term_id.id or False
					partner_addr = partner.address_get(['default', 'invoice', 'delivery', 'contact'])
					pricelist = partner.property_product_pricelist.id
				if False in partner_addr.values():
					raise Warning(_('No address(es) defined for this customer.'))
				vals = {
					'origin': _('Opportunity: %s') % str(case.id),
					'team_id': case.team_id and case.team_id.id or False,
					'categ_ids': [(6, 0, [categ_id.id for categ_id in case.tag_ids])],
					'partner_id': partner.id,
					'pricelist_id': pricelist,
					'partner_invoice_id': partner_addr['invoice'],
					'partner_shipping_id': partner_addr['delivery'],
					'date_order': fields.datetime.now(),
					'fiscal_position': fpos,
					'payment_term':payment_term,
					'is_property':True,
					}
				if partner.id:
					vals['user_id'] = partner.user_id and partner.user_id.id or self._uid
				if case.property_id:
					pro_sale_vals = {
							'origin': 'crm.lead',
							'property_id' :case.property_id.id,
							'name' : case.property_id.name or "" ,
							'product_uom_qty' : 1,
							'price_unit':case.property_id.sale_price or 0.0,
							'is_property':True,
							}
					vals.update({'order_line': [(0, 0, pro_sale_vals)]})
					case.property_id.write({'state':'sold'})
				new_id = self.env['sale.order'].create(vals)
				case.write({'ref': 'sale.order,%s' % new_id.id})
				new_ids.append(new_id.id)
				message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (new_id.name)
				case.message_post(body=message)
			if make.close:
				case.case_mark_won()
			if not new_ids:
				return {'type': 'ir.actions.act_window_close'}
			if len(new_ids)<=1:
				value = {
					'domain': str([('id', 'in', new_ids)]),
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'sale.order',
					'view_id': False,
					'type': 'ir.actions.act_window',
					'name' : _('Quotation'),
					'res_id': new_ids and new_ids[0]
				}
			else:
				value = {
					'domain': str([('id', 'in', new_ids)]),
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'sale.order',
					'view_id': False,
					'type': 'ir.actions.act_window',
					'name' : _('Quotation'),
					'res_id': new_ids
				}
			return value


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
