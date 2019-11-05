openerp.sale_order_dates_view_usability = function (instance) {
    instance.web_calendar.CalendarView = instance.web_calendar.CalendarView.extend({
        event_data_transform: function (event) {
            var res = this._super.apply(this, arguments);
        if (event.requested_date ) {
            var matches = res.className.match(/calendar_color_[0-9]*/g);
                if (matches.length)
                    var original_class_color = (matches[0].replace("calendar", "underline"));
            // set all obj with original_class_color class to event.hex_value for underline_color_x
            var x = document.getElementsByClassName(original_class_color);
            for (var j=0; j<x.length; j++) {
//                x[j].style.backgroundColor = 'green'; //no color for label
                x[j].classList.remove(original_class_color);
            }
            var requested_date = new Date(
                parseInt(event.requested_date.slice(0, 4)), // year
                parseInt(event.requested_date.slice(5, 7)) - 1, // fix js count month from 0
                parseInt(event.requested_date.slice(8, 10)), // date
                );
            var today = new Date();
            var four_days_from_today = new Date();
            var seven_days_from_today = new Date();
            var pastDate = today.getDate() + 4;
            four_days_from_today.setDate(pastDate);
            var pastDate = today.getDate() + 7;
            seven_days_from_today.setDate(pastDate);
            if (requested_date < today) {
                res.backgroundColor = 'red';
            }else if (requested_date <= four_days_from_today) {
                res.backgroundColor = 'orange';
            }else if (requested_date <= seven_days_from_today) {
                res.backgroundColor = 'yellow';
            }else{
                res.backgroundColor = 'green';
            }
        }
        return res;
        }
    });

};