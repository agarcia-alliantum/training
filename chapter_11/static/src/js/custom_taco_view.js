odoo.define('chapter_11.CustomTacoFormView', function (require) {
"use strict";

var CustomTacoFormController = require('chapter_11.CustomTacoFormController');
var CustomTacoFormRenderer = require('chapter_11.CustomTacoFormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var CustomTacoFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: CustomTacoFormController,
        Renderer: CustomTacoFormRenderer,
    }),
});

viewRegistry.add('product_configurator_form', CustomTacoFormView);

return CustomTacoFormView;

});