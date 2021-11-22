# -*- coding: utf-8 -*-
from operator import index
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    is_taco = fields.Boolean('Is Taco?', default=False)

    available_categ_id = fields.Integer('available_categ_id', compute='_compute_available_categ_id')

    @api.depends('is_taco')
    def _compute_available_categ_id(self):
        for l in self:
            if l.is_taco:
                l.available_categ_id = 15
            else:
                l.available_categ_id = False

    # FIX: How to change the domain in Quotation Templates Form at Lines panel?
    def _domain_line_ids(self):
        if self.is_taco != True:
            return [
                ('product_id.sale_ok', '=', True),
                ('product_id.categ_id', '=', self.env.ref('chapter_11.product_category_ingredients').id)
            ]
        return [
            ('product_id.sale_ok', '=', True),
        ]

    sale_order_template_line_ids = fields.One2many('sale.order.template.line',
        'sale_order_template_id',
        'Lines',
        copy=True,
        domain=_domain_line_ids
    )

    def write(self, values):
        response = super(models.Model, self).write(values)
        max_ingrs = self.env.company.sudo().max_ingredients
        if self.is_taco and len(self.sale_order_template_line_ids) > max_ingrs:
             raise ValidationError(_('Sorry but there is a maximum of %s ingredients for every custom Taco. Please remove the surplus.') % (max_ingrs))
        else:
            return response

class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'

    unavailable_in = fields.Char('Seasonal restiction', compute='_compute_unavailable_in')
    @api.depends('product_id')
    def _compute_unavailable_in(self):
        for line in self:
            line.unavailable_in = line.product_id.unavailable_in

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_taco = fields.Boolean('Is Taco?', default=False)

    def _get_product_domain(self):
        categ_ids = [self.env.ref('chapter_11.product_category_ingredients').id]
        return {
            'product_id': [
                ('sale_ok', '=', True),
                ('categ_id', 'in', categ_ids),
            ]
        }

    def _get_template_type(self):
        if self.is_taco:
            return 'TACO'
        else:
            return 'Quotation Template'

    @api.onchange('is_taco')
    def onchange_is_taco(self):
        result = {}
        if self.is_taco:
            result = {
                'domain': {
                    'sale_order_template_id': [('is_taco', '=', True)],
                    'order_line': self._get_product_domain(),
                }
            }
        else:
            result = {
                'domain': {
                    'sale_order_template_id': [],
                    'order_line': [],
                }
            }
        return result

    def add_custom_taco(self):
        #warning = {
        #    'title': 'Warning',
        #    'message': 'Open Wizard',
        #}
        #action = {'warning': warning}
        ctx = {
            'active_ids': self.env.context.get('active_ids', False),
            'order_id': self.env.context.get('params',{}).get('id',False)
        }
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'custom.taco.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        _logger.info("add_custom_taco\n\n%r\n\n",self.env.context)
        _logger.info("add_custom_taco\n\n%r\n\n",action)
        return action

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

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        super(SaleOrder, self).onchange_sale_order_template_id()
        if self.date_order and self.order_line:
            # Calculating the season of the date_order
            Y = 2000 #dummy year
            seasons = [
                ('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
                ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
                ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
                ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
                ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))
            ]
            #_date = self.date_order
            #if isinstance(_date, datetime):
            #    _date = _date.date()
            #_date = _date.replace(year=Y)
            #season = next(season for season, (start, end) in seasons if start <= _date <= end)
            season = self.get_season(self.date_order)
            _logger.info('\n\n\nSEEEEEEASOOOOOOOOON %s', season)
            # REMOVE OUT OF SEASON INGREDIENTS
            ids = [(3,l.id) for l in self.order_line if l.unavailable_in==season]
            if ids:
                _logger.info('try to delete %r', ids)
                self.order_line = ids

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    unavailable_in = fields.Char('Seasonal', compute='_compute_unavailable_in')
    is_ingredient = fields.Boolean('Ingredient', compute='_compute_is_ingredient')
    ingredients = fields.One2many('sol.ingredients', 'taco_id', 'Ingredients')

    @api.depends('ingredients')
    def _compute_is_ingredient(self):
        for line in self:
            line.is_ingredient = len(line.ingredients)>0

    @api.depends('product_id')
    def _compute_unavailable_in(self):
        for line in self:
            if line.product_id:
                line.unavailable_in = line.product_id.unavailable_in
            else:
                line.unavailable_in = False

    @api.onchange('product_id', 'product_uom_qty')
    def product_id_qty_change(self):
        action = {}
        if self.env.context.get('open_custom_taco'):
            #action = {'domain': {
            #    'product_id': [('default_code', '=like', 'ingredient')]
            #}}
            #warning = {}
            #warning['title'] = _("Warning")
            #warning['message'] = 'OPEN WIZARD'
            #action = {'warning': warning}
            ctx = {
                'active_ids': self.env.context.get('active_ids', False),
            }
            action = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'custom.taco.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }
            #action = self.env.ref('chapter_11.action_view_send_to_invoice').read()[0]
            #return action

            _logger.info("TACO\n\n%r\n\n",action)
        return action

class SOLineIngredientes(models.Model):
    _name = 'sol.ingredients'
    _description = 'Sale Order Line ingredients'

    taco_id = fields.Many2one('sale.order.line', 'Taco')
    ingredient_id = fields.Many2one('product.product', 'Ingredient')
    color = fields.Integer(string='Color', compute='_compute_color')
    name = fields.Char('Name',compute='_compute_color')
    description = fields.Char('Desciption',compute='_compute_color')

    @api.depends('ingredient_id')
    def _compute_color(self):
        for record in self:
            if record.ingredient_id:
                if record.ingredient_id.taco_color or record.ingredient_id.taco_color==0:
                    record.color = int(record.ingredient_id.taco_color)
                else:
                    record.color = record.ingredient_id.id % 12
                record.name = record.ingredient_id.default_code
                record.description = record.ingredient_id.name
            else:
                record.color = False
                record.name = False
                record.description = False



