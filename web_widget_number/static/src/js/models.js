/*******************************************************************************
See __openerp__.py file for Copyright and Licence Informations.
*******************************************************************************/

openerp.web_widget_number = function (instance) {

    instance.web.form.FieldFloat = instance.web.form.FieldFloat.extend({
        /***********************************************************************
        Overload section 
        ***********************************************************************/

        /**
         * Overload : 'start' function to catch 'blur' events.
         */
        start: function() {
            this.on("blurred", this, this._translate_comma);
            return this._super();
        },

        _translate_comma: function() {
            var val
            debugger;
            val = this.$el.find('input').attr('value');
            currenttxt = val.toString().replace(/,/g,'.');
            if (currenttxt){
                var value
                try {
                     value = eval(currenttxt);
                }catch (e) {}
                if (typeof (value) != 'undefined'){
                    this.set_value(value);
                    this.render_value();
                }
            }
        },

    });
};
