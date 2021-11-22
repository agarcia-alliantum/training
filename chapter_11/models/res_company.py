# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"


    max_ingredients = fields.Integer(default=10, string="Max ingredients")
    _sql_constraints = [('check_max_ingredients', 'CHECK(max_ingredients > 0)', 'Max Ingredients is required and must be greater than 0.')]


