odoo.define('sismatix_report', function (require) {
"use strict";

    var session = require('web.session');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');

    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var QWeb = core.qweb;

    var _t = core._t;

    Sidebar.include({

        redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (self.getParent().ViewManager.active_view.type == 'list') {
                self.$el.find('.o_dropdown').last().append(QWeb.render('WebPrintTreeViewPdf', {widget: self}));
                self.$el.find('.print_treeview_Pdf').on('click', self.on_sidebar_print_treeview_pdf);
            }
        },

        on_sidebar_print_treeview_pdf: function () {
            
            
            var self = this,
                view = this.getParent(),
                children = view.getChildren();
            if (children) {
                children.every(function (child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
            var export_columns_keys = [];
            /* fields string*/
            var export_columns_names = [];
            /*fields real names */
            var export_fields_names = [];
            $.each(view.visible_columns, function () {
                if (this.tag == 'field' && (this.widget === undefined || this.widget != 'handle')) {
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                    export_fields_names.push(this.name);
                }
            });
            var export_rows = [];
            $.blockUI();
            if (children) {
                // find only rows with data
                view.$el.find('.o_list_view > tbody > tr[data-id]:has(.o_list_record_selector input:checkbox:checked)')
                .each(function () {
                    var $row = $(this);
                    var export_row = [];
                    $.each(export_columns_keys, function () {
                        var $cell = $row.find('td[data-field="' + this + '"]')
                        var $cellcheckbox = $cell.find('.o_checkbox input:checkbox');
                        if ($cellcheckbox.length) {
                            export_row.push(
                                $cellcheckbox.is(":checked")
                                ? _t("True") : _t("False")
                            );
                        }
                        else {
                            var text = $cell.text().trim();
                            if ($cell.hasClass("o_list_number")) {
                                export_row.push(parseFloat(
                                    text
                                    // Remove thousands separator
                                    .split(_t.database.parameters.thousands_sep)
                                    .join("")
                                    // Always use a `.` as decimal separator
                                    .replace(_t.database.parameters.decimal_point, ".")
                                    // Remove non-numeric characters
                                    .replace(/[^\d\.-]/g, "")
                                ));
                            }
                            else {
                                export_row.push(text);
                            }
                        }
                    });
                    export_rows.push(export_row);
                });
            }

            view.session.get_file({
                url: '/web/download/pdf_view',
                data: {data: JSON.stringify({
                    model: view.model,
                    headers: export_columns_names,
                    rows: export_rows,
                    headers_names: export_fields_names,
                })},
                complete: $.unblockUI
            });
            
        }

    });
});
