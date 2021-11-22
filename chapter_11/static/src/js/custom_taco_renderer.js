odoo.define('chapter_11.CustomTacoFormRenderer', function (require) {
    "use strict";
    
    var FormRenderer = require('web.FormRenderer');
    var CustomTacoMixin = require('chapter_11.CustomTacoMixin');
    
    var CustomTacoFormRenderer = FormRenderer.extend(CustomTacoMixin ,{
        events: {},
        init: function (){
            this._super.apply(this, arguments);            
        },       
        start: function () {
            this._super.apply(this, arguments);            
        },
        renderCustom: function (configuratorHtml) {            
        },
    });

    return CustomTacoFormRenderer;
});