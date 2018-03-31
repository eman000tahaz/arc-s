# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MainteneceItem(models.Model):
    _name = "maintenance.item"

    name = fields.Char('Name')
    desc = fields.Char('Description')
    cost = fields.Float('Cost')
    quantity = fields.Integer('Quantity')
    maintenance_id = fields.Many2one('property.maintenance', string='Maintenance')