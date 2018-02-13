odoo.define('sismatix_report.framework', function (require) {
"use strict";

var core = require('web.core');
var crash_manager = require('web.crash_manager');
var ajax = require('web.ajax');
var Widget = require('web.Widget');
var _t = core._t;

function redirect (url, wait) {
    // Dont display a dialog if some xmlhttprequest are in progress
    crash_manager.disable();

    var load = function() {
        var old = "" + window.location;
        var old_no_hash = old.split("#")[0];
        var url_no_hash = url.split("#")[0];
        location.assign(url);
        if (old_no_hash === url_no_hash) {
            location.reload(true);
        }
    };

    var wait_server = function() {
        ajax.rpc("/web/webclient/version_info", {}).done(load).fail(function() {
            setTimeout(wait_server, 250);
        });
    };

    if (wait) {
        setTimeout(wait_server, 1000);
    } else {
        load();
    }
}


function logout() {
    /*ADD return View method */
    var my_Model = require('web.Model');
    var change_tree_view = new my_Model('change.tree.fields');
    change_tree_view.call('return_view');
    redirect('/web/session/logout');
    return $.Deferred();
}
core.action_registry.add("logout", logout);

});

