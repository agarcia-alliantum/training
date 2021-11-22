odoo.define('chapter_11.CustomTacoModal', function (require) {
    "use strict";

var ajax = require('web.ajax');
var Dialog = require('web.Dialog');
var ServicesMixin = require('web.ServicesMixin');
var CustomTacoMixin = require('chapter_11.CustomTacoMixin');
var weContext = require('web_editor.context');

var productNameMap = {};
var CustomTacoMap = {};

var CustomTacoModal = Dialog.extend(ServicesMixin, CustomTacoMixin, {});

return CustomTacoModal;
})