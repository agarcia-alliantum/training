console.log('TACO CONTROLLER 1');
odoo.define('chapter_11.CustomTacoFormController', function (require) {
    "use strict";
    
    var core = require('web.core');
    var _t = core._t;
    var FormController = require('web.FormController');
    //var CustomTacoModal = require('chapter_11.CustomTacoModal');
    
    var CustomTacoFormController = FormController.extend({
        _onButtonClicked: function (event) {
            console.log('TACO CONTROLLER _onButtonClicked', event);
            this._super.apply(this, arguments); 
        },
        init: function (){
            console.log('INIT TACO CONTROLLER');
            console.log('THIS,ARG', this, arguments);
            this._super.apply(this, arguments);  
        },
    });

    return CustomTacoFormController;
})