odoo.define('mis_builder_xlsx_exploded.widget', function (require) {
"use strict";

var MisBuilderWidget = require('mis_builder.widget');

MisBuilderWidget.include({
    events: _.extend({}, MisBuilderWidget.prototype.events, {
        "click .oe_mis_builder_export_exploded": "exportXlsExploded",
    }),
    exportXlsExploded: function () {
        var self = this;
        var context = self.getParent().state.context;
        this._rpc({
            model: "mis.report.instance",
            method: "export_xls_exploded",
            args: [this._instanceId()],
            context: context,
        }).then(function (result) {
            self.do_action(result);
        });
    },
});

});
