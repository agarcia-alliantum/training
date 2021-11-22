
odoo.define('chapter_11.taco_and_section_and_note_backend', function (require) {
    // The goal of this file is to contain JS hacks related to allowing
    // section and note on sale order and invoice.

    // [UPDATED] now also allows configuring products on sale order.

    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var FieldChar = require('web.basic_fields').FieldChar;
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fieldRegistry = require('web.field_registry');
    var ListFieldText = require('web.basic_fields').ListFieldText;
    var ListRenderer = require('web.ListRenderer');

    var SectionAndNoteListRenderer = ListRenderer.extend({
        /**
         * We want section and note to take the whole line (except handle and trash)
         * to look better and to hide the unnecessary fields.
         *
         * @override
         */
        _renderBodyCell: function (record, node, index, options) {
            var $cell = this._super.apply(this, arguments);

            var isSection = record.data.display_type === 'line_section';
            var isNote = record.data.display_type === 'line_note';

            if (isSection || isNote) {
                if (node.attrs.widget === "handle") {
                    return $cell;
                } else if (node.attrs.name === "name") {
                    var nbrColumns = this._getNumberOfCols();
                    if (this.handleField) {
                        nbrColumns--;
                    }
                    if (this.addTrashIcon) {
                        nbrColumns--;
                    }
                    $cell.attr('colspan', nbrColumns);
                } else {
                    $cell.removeClass('o_invisible_modifier');
                    return $cell.addClass('o_hidden');
                }
            }

            return $cell;
        },

        _getPricelistId: function () {
            var saleOrderForm = this.getParent() && this.getParent().getParent();
            var stateData = saleOrderForm && saleOrderForm.state && saleOrderForm.state.data;
            var pricelist_id = stateData.pricelist_id && stateData.pricelist_id.data && stateData.pricelist_id.data.id;

            return pricelist_id;
        },


        _productsToRecords: function (products) {
            console.log('_productsToRecords', products)
        },

        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);

            if (record.data.display_type) {

                if(record.data.display_type === 'open_taco_configurator') {
                    console.log('OPEN DE WIZARD')
                    var self = this;
                    var pricelistId = self._getPricelistId();
                    this.do_action({
                        name: "Custom Taco",
                        type: 'ir.actions.act_window',
                        res_model: 'custom.taco.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}},
                    },{
                        on_close: function (products) {
                            console.log('ON CLOSE', products)
                        }
                    }).then(function(response) {
                        console.log('OPEN WIZARD MODAL RESPONSE', response);
                    });
                    return $row;
                }
                $row.addClass('o_is_' + record.data.display_type);
            }

            return $row;
        },
        /**
         * We want to add .o_section_and_note_list_view on the table to have stronger CSS.
         *
         * @override
         * @private
         */

        _onAddRecord: function (ev) {
            //ev.preventDefault();
            //ev.stopPropagation();

            console.log('ON ADD RECORD', ev);
            console.log(this.state)
            return this._super.apply(this, arguments);
        },
        _renderView: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$('.o_list_table').addClass('o_section_and_note_list_view');
            });
        }
    });

    // We create a custom widget because this is the cleanest way to do it:
    // to be sure this custom code will only impact selected fields having the widget
    // and not applied to any other existing ListRenderer.
    var SectionAndNoteFieldOne2Many = FieldOne2Many.extend({
        /**
         * We want to use our custom renderer for the list.
         *
         * @override
         */
        _getRenderer: function () {
            if (this.view.arch.tag === 'tree') {
                return SectionAndNoteListRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });

    // This is a merge between a FieldText and a FieldChar.
    // We want a FieldChar for section,
    // and a FieldText for the rest (product and note).
    var SectionAndNoteFieldText = function (parent, name, record, options) {
        var isSection = record.data.display_type === 'line_section';
        var Constructor = isSection ? FieldChar : ListFieldText;
        return new Constructor(parent, name, record, options);
    };

    fieldRegistry.add('taco_and_section_and_note_one2many', SectionAndNoteFieldOne2Many);
    fieldRegistry.add('section_and_note_text', SectionAndNoteFieldText);

    return SectionAndNoteListRenderer;
    });
