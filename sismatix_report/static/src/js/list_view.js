odoo.define('sismatix_report.ListView', function (require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var data_manager = require('web.data_manager');
var DataExport = require('web.DataExport');
var formats = require('web.formats');
var common = require('web.list_common');
var Model = require('web.DataModel');
var Pager = require('web.Pager');
var pyeval = require('web.pyeval');
var session = require('web.session');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var View = require('web.View');

var Class = core.Class;
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;
var list_widget_registry = core.list_widget_registry;

var webList = require('web.ListView');


webList.include({
    _template: 'ListView',
    render_sidebar: function($node) {
        if (!this.sidebar && this.options.sidebar) {
            this.sidebar = new Sidebar(this, {editable: this.is_action_enabled('edit')});
            if (this.fields_view.toolbar) {
                this.sidebar.add_toolbar(this.fields_view.toolbar);
            }
            this.sidebar.add_items('other', _.compact([
                { label: _t("Export"), callback: this.on_sidebar_export },
                {label: _t("Change Tree View"), callback: this.on_change_tree },
                this.fields_view.fields.active && {label: _t("Archive"), callback: this.do_archive_selected},
                this.fields_view.fields.active && {label: _t("Unarchive"), callback: this.do_unarchive_selected},
                this.is_action_enabled('delete') && { label: _t('Delete'), callback: this.do_delete_selected }
            ]));

            $node = $node || this.options.$sidebar;
            this.sidebar.appendTo($node);

            // Hide the sidebar by default (it will be shown as soon as a record is selected)
            this.sidebar.do_hide();
        }
    },
    on_change_tree: function() {
        /*var my_Model = require('web.Model');
        var change_tree_view = new Model('change.tree.fields');
        change_tree_view.call('open_view');*/
        var self = this;
        var current_fields = [];
        for (var key in self.fields_view.fields) {
            current_fields.push(key);    
        };
        console.log(current_fields);
        var action = {
            type: 'ir.actions.act_window',
            res_model: 'change.tree.fields',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                'default_model': self.model,
                'default_view_id': self.fields_view.view_id,
                'default_def_fields': self.fields_view.fields,
                'default_current_fields': current_fields,
            },
        };
        self.do_action(action);
        
    },
});

});


