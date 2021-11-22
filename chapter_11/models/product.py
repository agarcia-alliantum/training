# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    unavailable_in = fields.Selection(string='Seasonal availability',
        selection=[
            ('never', 'All seasons available'),
            ('winter', 'Not in Winter'),
            ('spring', 'Not in Spring'),
            ('autumn', 'Not in Autumn'),
            ('summer', 'Not in Summer'),
        ],
        default='never'
    )

    taco_color = fields.Integer(string='Ingredient color',
        default=0,
    )

    #selection= [
    #    ('0', 'white'),
    #    ('1', 'ligth red'),
    #    ('2', 'orange'),
    #    ('3', 'yellow'),
    #    ('4', 'ligth blue'),
    #    ('5', 'purple'),
    #    ('6', 'pink'),
    #    ('7', 'turquoise'),
    #    ('8', 'blue'),
    #    ('9', 'red'),
    #    ('10', 'ligth green'),
    #    ('11', 'ligth purple'),
    #],
