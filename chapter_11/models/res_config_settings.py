# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    max_ingredients = fields.Integer(
        related='company_id.max_ingredients',
        string="Max ingredients for custom Taco",
        readonly=False
    )