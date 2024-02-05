this.ckan.module('daterangepicker-module', function($, _) {
    return {
	    options:{
			    ranges: {
                   'Today': [moment().startOf('day'), moment().endOf('day')],
                   'Yesterday': [(moment().subtract('days', 1)).startOf('day'), (moment().subtract('days', 1)).endOf('day')],
                   'Last 7 Days': [moment().subtract('days', 7), moment()],
                   'Last 30 Days': [moment().subtract('days', 30), moment()],
                   'This Month': [moment().startOf('month'), moment().endOf('month')],
                   'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
                },
				dateTimeFormat: 'YYYY-MM-DD, HH:mm:ss',
				separator: ' / ',
				timePickerIncrement: 1,
                startDate: moment().subtract('days', 31),
                endDate: moment(),
                showDropdowns: false,
                timePicker: true,
				timePicker12Hour: false
		},
        initialize: function() {

            // Add hidden <input> tags #ext_startdate and #ext_enddate,
            // if they don't already exist.
            var form = $("#dataset-search");
            // CKAN 2.1
            if (!form.length) {
                form = $(".search-form");
            }

            if ($("#ext_startdate").length === 0) {
                $('<input type="hidden" id="ext_startdate" name="ext_startdate" />').appendTo(form);
            }
            if ($("#ext_enddate").length === 0) {
                $('<input type="hidden" id="ext_enddate" name="ext_enddate" />').appendTo(form);
            }
			
			var url = decodeURIComponent(location.search);
			var params = url.replace(/^\?/,'').replace(/&amp;/g,'&').split("&");
			var startDate, endDate;
			
			for (var j=0; j < params.length; j++) {
				var param = params[j].split("=");
				if(param[0]){
					switch ( param[0] ) {
						case "ext_startdate": 
										var p = param[1];
										startDate = p;
										break;
						case "ext_enddate": 
										var p = param[1];
										endDate = p;										
										break;
						default :       break;      
										
					}
				}
			}	
			
			// //////////////////////////////////////////////////////////////////
			// Set the previously selected date range inside the temporal form
			// //////////////////////////////////////////////////////////////////
			if(startDate && endDate){
				// Set the value of the hidden <input id="ext_startdate"> to
                // the chosen start date.
                $('#ext_startdate').val(startDate);

                // Set the value of the hidden <input id="ext_enddate"> to
                // the chosen end date.
                $('#ext_enddate').val(endDate);
								
				if(startDate.indexOf('Z') != -1){
					startDate = startDate.substring(0, startDate.indexOf('Z'));
				}
				
				if(endDate.indexOf('Z') != -1){
					endDate = endDate.substring(0, endDate.indexOf('Z'));
				}
				
				$('#daterange').val(moment(startDate).format(this.options.dateTimeFormat) + this.options.separator + moment(endDate).format(this.options.dateTimeFormat));  
			}
			
            // Add a date-range picker widget to the <input> with id #daterange
            $('input[id="daterange"]').daterangepicker({
                ranges: this.options.ranges,
				dateTimeFormat: this.options.dateTimeFormat,
				separator: this.options.separator,
				timePickerIncrement: this.options.timePickerIncrement,
				startDate: startDate ? moment(startDate) : this.options.startDate,
                endDate: endDate ? moment(endDate) : this.options.endDate,				
                showDropdowns: this.options.showDropdowns,
                timePicker: this.options.timePicker,
                timePicker12Hour: this.options.timePicker12Hour
            },
            function(start, end) {
                console.log('datesearch function started')
                // Bootstrap-daterangepicker calls this function after the user
                // picks a start and end date.

                // Format the start and end dates into strings in a date format
                // that Solr understands.
                start = start.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
                end = end.format('YYYY-MM-DDTHH:mm:ss') + 'Z';

                // Set the value of the hidden <input id="ext_startdate"> to
                // the chosen start date.
                $('#ext_startdate').val(start);

                // Set the value of the hidden <input id="ext_enddate"> to
                // the chosen end date.
                $('#ext_enddate').val(end);

                // Submit the <form id="dataset-search">.
                setTimeout(function() {
                    console.log('submit form for datesearch')
                    form.submit();
                  }, 800);
                //$("#dataset-search").submit();
            });
        }
    }
});
