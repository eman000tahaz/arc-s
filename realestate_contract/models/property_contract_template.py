# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from tkFileDialog import asksaveasfilename
# import os.path
# from docx import Document

class PropertyContractTemlate(models.Model):
	_name = "property.contract.template"

	tenancy_id = fields.Many2one('account.analytic.account', string='Tenancy', domain=[('is_property','=','True')])
	temp = fields.Html('Template')

	@api.onchange('tenancy_id')
	def _get_template_text(self):
		text = '<p align="center" style="font-size: 14px;"><b><u>عقد ابجار شقة</u></b></p>'
		text += '<p align="right" style="font-size: 13px;"><u>: تحرر هذا العقد بين كل من</u></p>'
		text += '<p align="right" style="font-size: 12px;">'+str(self.env.user.company_id.name)+' : اولا </p>'
		text += '<p align="right" style="font-size: 12px;">/     ويمثلها السيد   </p>'
		text += '<p align="left" style="font-size: 12px;">(طرف اول / مؤجر)</p>'
		text += '<p align="right" style="font-size: 12px;">'+str(self.tenancy_id.tenant_id.name)+'/ ثانيا : السيد </p>'
		text += '<p align="right" style="font-size: 12px;">'+str(self.tenancy_id.tenant_id.country_id.name)+'       /الجنسية  </p>'
		text += '<p align="right" style="font-size: 12px;">'+str(self.tenancy_id.tenant_id.mobile)+'      / ت  </p>'
		text += '<p align="left" style="font-size: 12px;">(طرف ثان / مستأجر)</p>'
		self.temp = text

	# def do_print(self):
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print self.temp
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	print "                        "
	# 	# document = Document()
	# 	# document.add_paragraph(self.temp)
	# 	name = self.tenancy_id.name 
	# 	# document.save(name+'.html')
		# name = asksaveasfilename(defaultextension=".doc",
  #                        filetypes=[("Text files",".txt"),
  #                                   ("Word files",".doc")],
  #                        initialdir="dir",
  #                        title="Save as")
		# data = open(name+'.docx',"w")
		# text = self.temp
		# data.write(text)
		# data.close()