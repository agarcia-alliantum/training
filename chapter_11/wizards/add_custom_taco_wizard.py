# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class CustomTacoWizard(models.TransientModel):
    _name = 'custom.taco.wizard'
    _description = 'Add custom taco to SO'

    ingredients_limit = 10

    def _default_order_id(self):
        #_logger.info('\n\nCONTEXT:\n%r\n\n', self.env.context)
        order_id = self.env.context.get('order_id', self.env.context.get('active_id', self.env.context.get('active_ids',[])) )
        order = self.env['sale.order'].browse(order_id)
        return order

    order_id = fields.Many2one('sale.order', string='Order Reference', default=_default_order_id)

    taco_id = fields.Many2one(
        'sale.order.template',
        'Select existing Taco',
        domain="[('is_taco','=',True)]",
        context={'default_is_taco': True}
    )

    ingredients = fields.One2many(
        'product.product',
        string='Ingredients',
        compute='_compute_ingredients',
    )

    @api.depends('taco_id')
    def _compute_ingredients(self):
        for taco in self:
            if taco.taco_id:
                p_ids = [l.product_id.id for l in self.env['sale.order.template.line'].search([('sale_order_template_id','=',taco.taco_id.id)], limit=self.ingredients_limit)]
                taco.ingredients = self.env['product.product'].browse(p_ids)
            else:
                taco.ingredients = False

    @api.model
    def get_season(self, date_in):
        # Calculating the season of the date_order
        Y = 2000 #dummy year
        seasons = [
            ('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
            ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
            ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
            ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
            ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))
        ]
        _date = date_in
        if isinstance(_date, datetime):
            _date = _date.date()
        _date = _date.replace(year=Y)
        return next(season for season, (start, end) in seasons if start <= _date <= end)

    def send_to_order(self):
        if self.taco_id and self.ingredients:
            ingredients = []
            price_unit = 0.0
            #_logger.info('\n\nCONTEXT:\n%r\n\n', self.env.context)
            #_logger.info('\n\nDAAATEEEE:\n\n%r %r', self.order_id, self.order_id.date_order)
            season = self.get_season(self.order_id.date_order)
            for i in self.ingredients:
                if i.unavailable_in!=season:
                    price_unit += i.lst_price
                    ingredients.append((0, 0, {
                        'ingredient_id': i.id
                    }))
            self.order_id.order_line = [(0,0,{
                'product_id': self.env.ref('chapter_11.custom_taco_1').id,
                'name': '🌮 ' + _('Custom Taco') + ': ' + self.taco_id.name,
                'product_uom_qty': 1,
                'price_unit': price_unit,
                'ingredients': ingredients
            })]

    """
    sale_order_template_id = fields.Many2one(
        "sale.order.template", string="Default Sale Template",
        domain="['|', ('company_id', '=', False), ('company_id', '=', id)]",
        check_company=True,
    )

    def _default_order_id(self):
        order_id = self.env.context.get('order_id', self.env.context.get('active_ids',[]) )
        return self.env['sale.order'].browse(order_id)

    order_id = fields.Many2one('sale.order', string='Order Reference', default=_default_order_id)

    def send_to_order(self):
        if self.order_id:
            self.order_id.is_taco = True
            self.order_id.sale_order_template_id = self.sale_order_template_id
            self.order_id.onchange_is_taco()
            self.order_id.onchange_sale_order_template_id()

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True,
        copy=False,
        default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True, digits=(12, 6),
        readonly=True, help='The rate of the currency to the currency of rate 1 applicable at the date of the order')

    @api.depends('pricelist_id', 'date_order', 'company_id')
    def _compute_currency_rate(self):
        for order in self:
            if not order.company_id:
                order.currency_rate = order.currency_id.with_context(date=order.date_order).rate or 1.0
                continue
            elif order.company_id.currency_id and order.currency_id:  # the following crashes if any one is undefined
                order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.date_order)
            else:
                order.currency_rate = 1.0
    """


class CustomTacoLine(models.TransientModel):
    _name = 'custom.taco.line.wizard'
    _description = 'Lines for custom taco'

    order_id = fields.Many2one('custom.taco.wizard', string='Custom Taco')
    #name = fields.Char()
    #order_id = fields.Many2one('sale.order', string='Order Reference', related='wizard_id.order_id')
    #order_id = fields.Many2one('sale.order', string='Order Reference', compute='_compute_order_id')

    def _compute_order_id(self):
        return self.env['sale.order'].browse(self.env.context.get('active_ids',[]))

    def _get_product_domain(self):
        categ_ids = [self.env.ref('chapter_11.product_category_ingredients').id]
        return [
            ('sale_ok', '=', True),
            ('categ_id', 'in', categ_ids),
        ]

    @api.depends('product_uom_qty', 'product_id', 'price_unit')
    def _compute_amount(self):
        for line in self:
            if line.product_id:
                line.price_subtotal = line.price_unit * line.product_uom_qty
                line.product_uom = line.product_id.uom_id

    product_id = fields.Many2one (
        'product.product',
        'Ingredients',
        required=True,
        domain=_get_product_domain,
    )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)


