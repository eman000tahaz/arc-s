odoo.define('sismatix_report.FavoriteMenu', function (require) {
"use strict";

    var web = require('web.FavoriteMenu');
    var core = require('web.core');
    var data_manager = require('web.data_manager');
    var pyeval = require('web.pyeval');
    var session = require('web.session');
    var Widget = require('web.Widget');

    var _t = core._t;

    return Widget.extend({
        template: 'SearchView.FavoriteMenu',
        events: {
        'click li': function (event) {
            event.stopImmediatePropagation();
        },
        'click li a': function (event) {
            event.preventDefault();
        },
        /*ADD functions to new  buttons */
        'click .o_save_view a': function (event) {
            event.preventDefault();
            alert('prego');
        },
        /*'click .os_save_name button': 'save_favorite_view',
        'hidden.bs.dropdown': 'close_menus',
        'keyup .os_save_name input': function (ev) {
            if (ev.which === $.ui.keyCode.ENTER) {
                this.save_favorite_view();
            }*/
        
        /*************************************************************/
    },
    init: function (parent, query, target_model, action_id, filters) {
        this._super.apply(this,arguments);
        this.searchview = parent;
        this.query = query;
        this.target_model = target_model;
        this.action_id = action_id;
        this.filters = {};
        _.each(filters, this.add_filter.bind(this));
    },
    start: function () {
        alert('yeeee');
        return this._super();
    },
    
    });
    
});

/*odoo.define('web.FilterMenu', function (require) {
"use strict";

var data_manager = require('web.data_manager');
var search_filters = require('web.search_filters');
var search_inputs = require('web.search_inputs');
var Widget = require('web.Widget');

return Widget.extend({
    template: 'SearchView.FilterMenu',
    events: {
        'click .o_add_filter': function (event) {
            event.preventDefault();
            this.toggle_custom_filter_menu();
        },
        'click li': function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();
        },
        'hidden.bs.dropdown': function () {
            this.toggle_custom_filter_menu(false);
        },
        'click .o_add_condition': 'append_proposition',
        'click .o_apply_filter': 'commit_search',
        'keyup .o_searchview_extended_prop_value': function (ev) {
            if (ev.which === $.ui.keyCode.ENTER) {
                this.commit_search();
            }
        },
    },
    init: function (parent, filters) {
        this._super(parent);
        this.filters = filters || [];
        this.searchview = parent;
        this.propositions = [];
        this.custom_filters_open = false;
    },
    start: function () {
        var self = this;
        this.$menu = this.$('.o_filters_menu');
        this.$add_filter = this.$('.o_add_filter');
        this.$apply_filter = this.$('.o_apply_filter');
        this.$add_filter_menu = this.$('.o_add_filter_menu');
        _.each(this.filters, function (group) {
            if (group.is_visible()) {
                group.insertBefore(self.$add_filter);
                $('<li class="divider">').insertBefore(self.$add_filter);
            }
        });
    },
    get_fields: function () {
        if (!this._fields_def) {
            this._fields_def = data_manager.load_fields(this.searchview.dataset).then(function (data) {
                var fields = {
                    id: { string: 'ID', type: 'id', searchable: true }
                };
                _.each(data, function(field_def, field_name) {
                    if (field_def.selectable !== false && field_name !== 'id') {
                        fields[field_name] = field_def;
                    }
                });
                return fields;
            });
        }
        return this._fields_def;
    },
    toggle_custom_filter_menu: function (is_open) {
        var self = this;
        this.custom_filters_open = !_.isUndefined(is_open) ? is_open : !this.custom_filters_open;
        var def;
        if (this.custom_filters_open && !this.propositions.length) {
            def = this.append_proposition();
        }
        $.when(def).then(function () {
            self.$add_filter
                .toggleClass('o_closed_menu', !self.custom_filters_open)
                .toggleClass('o_open_menu', self.custom_filters_open);
            self.$add_filter_menu.toggle(self.custom_filters_open);
            self.$('.o_filter_condition').toggle(self.custom_filters_open);
        });
    },
    append_proposition: function () {
        var self = this;
        return this.get_fields().then(function (fields) {
            var prop = new search_filters.ExtendedSearchProposition(self, fields);
            self.propositions.push(prop);
            prop.insertBefore(self.$add_filter_menu);
            self.$apply_filter.prop('disabled', false);
            return prop;
        });
    },
    remove_proposition: function (prop) {
        this.propositions = _.without(this.propositions, prop);
        if (!this.propositions.length) {
            this.$apply_filter.prop('disabled', true);
        }
        prop.destroy();
    },
    commit_search: function () {
        var filters = _.invoke(this.propositions, 'get_filter'),
            filters_widgets = _.map(filters, function (filter) {
                return new search_inputs.Filter(filter, this);
            }),
            filter_group = new search_inputs.FilterGroup(filters_widgets, this.searchview),
            facets = filters_widgets.map(function (filter) {
                return filter_group.make_facet([filter_group.make_value(filter)]);
            });
        filter_group.insertBefore(this.$add_filter);
        $('<li class="divider">').insertBefore(this.$add_filter);
        this.searchview.query.add(facets, {silent: true});
        this.searchview.query.trigger('reset');

        _.invoke(this.propositions, 'destroy');
        this.propositions = [];
        this.append_proposition();
        this.toggle_custom_filter_menu(false);
    },
});

});

odoo.define('web.GroupByMenu', function (require) {
"use strict";

var core = require('web.core');
var data_manager = require('web.data_manager');
var search_inputs = require('web.search_inputs');
var Widget = require('web.Widget');

var QWeb = core.qweb;

return Widget.extend({
    template: 'SearchView.GroupByMenu',
    events: {
        'click li': function (event) {
            event.stopImmediatePropagation();
        },
        'hidden.bs.dropdown': function () {
            this.toggle_add_menu(false);
        },
        'click .o_add_custom_group a': function (event) {
            event.preventDefault();
            this.toggle_add_menu();
        },
    },
    init: function (parent, groups) {
        this._super(parent);
        this.groups = groups || [];
        this.groupable_fields = [];
        this.searchview = parent;
    },
    start: function () {
        this.$menu = this.$('.o_group_by_menu');
        var divider = this.$menu.find('.divider');
        _.invoke(this.groups, 'insertBefore', divider);
        if (this.groups.length) {
            divider.show();
        }
        this.$add_group = this.$menu.find('.o_add_custom_group');
    },
    get_fields: function () {
        var self = this;
        if (!this._fields_def) {
            this._fields_def = data_manager.load_fields(this.searchview.dataset).then(function (fields) {
                var groupable_types = ['many2one', 'char', 'boolean', 'selection', 'date', 'datetime'];
                var filter_group_field = _.filter(fields, function(field, name) {
                    if (field.store && _.contains(groupable_types, field.type)) {
                        field.name = name;
                        return field;
                    }
                });
                self.groupable_fields = _.sortBy(filter_group_field, 'string');

                self.$menu.append(QWeb.render('GroupByMenuSelector', self));
                self.$add_group_menu = self.$('.o_add_group');
                self.$group_selector = self.$('.o_group_selector');
                self.$('.o_select_group').click(function () {
                    self.toggle_add_menu(false);
                    var field = self.$group_selector.find(':selected').data('name');
                    self.add_groupby_to_menu(field);
                });
            });
        }
        return this._fields_def;
    },
    toggle_add_menu: function (is_open) {
        var self = this;
        this.get_fields().then(function () {
            self.$add_group
                .toggleClass('o_closed_menu', !(_.isUndefined(is_open)) ? !is_open : undefined)
                .toggleClass('o_open_menu', is_open);
            self.$add_group_menu.toggle(is_open);
            if (self.$add_group.hasClass('o_open_menu')) {
                self.$group_selector.focus();
            }
        });
    },
    add_groupby_to_menu: function (field_name) {
        var filter = new search_inputs.Filter({attrs:{
            context:"{'group_by':'" + field_name + "''}",
            name: _.find(this.groupable_fields, {name: field_name}).string,
        }}, this.searchview);
        var group = new search_inputs.FilterGroup([filter], this.searchview),
            divider = this.$('.divider').show();
        group.insertBefore(divider);
        group.toggle(filter);
    },
});

});
*/