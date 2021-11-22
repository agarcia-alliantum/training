odoo.define('chapter_11.CustomTacoMixin', function (require) {
    'use strict';
    
    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var utils = require('web.utils');
    var ajax = require('web.ajax');
    var _t = core._t;
    
    var CustomTacoMixin = {
        events: {},
        
    };

    return CustomTacoMixin;
})