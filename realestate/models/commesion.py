# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class property_commession(models.Model):
    _name = "property.commession"

    name = fields.Char('Commession Name',required=True)
    value = fields.Float('Commession Value in Percent (10%)',required=True)
    journal_id = fields.Many2one('account.journal','Journal',required=True)
    management_journal_id = fields.Many2one('account.journal','Management Company Journal')



class account_asset_asset(models.Model):
    _inherit = "account.asset.asset"

    property_commession = fields.Many2one('property.commession', 'Property Commession', help='Property Commession.')


