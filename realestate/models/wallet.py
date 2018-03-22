# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Wallet(models.Model):
    _name = "realestate.wallet"

    name = fields.Char('Name')
    property_ids = fields.One2many('account.asset.asset', 'wallet_id', string='Properties')