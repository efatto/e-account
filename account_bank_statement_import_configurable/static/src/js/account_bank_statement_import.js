/******************************************************************************
* Copyright 2018 MuK IT GmbH
* Copyright 2019 Enrico Ganzaroli (enrico.gz@gmail.com)
* Copyright 2019 Sergio Corato (https://efatto.it)
******************************************************************************/

odoo.define('account_bank_statement.import', function (require) {
"use strict";

var core = require('web.core');

var BaseImport = require('base_import.import');
var Model = require('web.Model');

var _t = core._t;
var QWeb = core.qweb;

var AccountBankStatementImport = BaseImport.DataImport.extend({
    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.filename = action.params.filename;
        this.parent_context = action.params.context || {};
        if (this.parent_context.separator) {
            this.separator = this.parent_context.separator;
        }
        if (this.parent_context.float_thousand_separator) {
            this.float_thousand_separator = this.parent_context.float_thousand_separator;
        }
        if (this.parent_context.float_decimal_separator) {
            this.float_decimal_separator = this.parent_context.float_decimal_separator;
        }
        action.display_name = _t('Import Bank Statement');
        this.Import = new Model('account.bank.statement.import.ex.wizard');
    },
    start: function () {
        var self = this;
        return this._super().then(function (res) {
        	self.loaded_file();
        });
    },
    create_model: function() {
    	return $.Deferred().resolve(this.parent_context.wizard_id);
    },
    onfile_loaded: function () {
        this.$('.oe_import_separator').val(this.separator);
        this.$('.oe_import_float_thousand_separator').val(this.float_thousand_separator);
        this.$('.oe_import_float_decimal_separator').val(this.float_decimal_separator);
    	this.$('.oe_import_file_show').val(this.filename);
        this.$('label[for=my-file-selector], input#my-file-selector').hide();
        this.$('label[for=my-file-selector]').parent().append(
        		$('<span/>' , {class: "btn btn-default disabled", text: "File loaded!"}));
        this.$('.oe_import_file_reload').hide();
        this.settings_changed();
    },
});

core.action_registry.add('import_bank_statement', AccountBankStatementImport);

});

