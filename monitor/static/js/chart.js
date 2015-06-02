function chart()
{

	this.mychart = null;
	this.interval_number = null;
	this.selected_metrics = null;
	this.chart_config =null;

    this.callback = null;

    this.hidden_status_prefix = "h_status--";

    this.get_selected_metrics = function()
    {
        return this.selected_metrics;
    }

    this.get_chart_config = function() 
    {
        return this.chart_config;
    }


    this.get_chart = function()
    {
        return this.mychart;
    }

	this.set_selected_metrics = function(new_selected_metrics)
	{
		this.selected_metrics = new_selected_metrics;
	}

	this.set_chart_config = function(new_chart_config)
	{
		this.chart_config = new_chart_config;
	}

	this.clear_chart = function()
	{
		if (this.chart_config != undefined) {
			$(this.chart_config['container_selector']).empty();
		};
        if (this.mychart != undefined) {
            this.mychart.destroy();
            this.mychart = null;
        };
        if (this.interval_number != undefined) {
            clearInterval(this.interval_number);
        }
	}

	this.set_highchart = function()
	{
		Highcharts.setOptions({
            global: {
                useUTC: this.chart_config['use_utc']
            }
        });
	}

    this.set_interval_num = function( tmp_interval_number )
    {
        this.interval_number = tmp_interval_number;
    }

    this.set_chart = function(tmp_chart)
    {
        this.mychart = tmp_chart;
    }

    this.set_callback = function(tmp_callback)
    {
        this.callback = tmp_callback;

    }

	// clear_chart();
	// set_highchart();

    this.init_ajax = null;
    this.update_ajax = null;

	this.create_chart = function()
    {

        $(this.chart_config['container_selector']).append('<button class="btn btn-lg btn-info"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</button>');

        create_highstock_chart = function(current_series_data,tmp_current_class,current_yAxis,current_tooltip,tmp_chart_config){
                 // $(tmp_current_class.get_chart_config()['container_selector']).highcharts({
                 $(tmp_chart_config['container_selector']).highcharts('StockChart',{
                    chart:{
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                // tmp_chart = this;
                                tmp_current_class.set_chart(this);
                                if (tmp_chart_config['update_flag']) {
                                    // tmp_interval_num[0] = setInterval(tmp_current_class.update,tmp_chart_config['frequency']*1000);
                                    var tmp_interval_num = setInterval(function()
                                        {
                                            tmp_current_class.update();
                                        },tmp_chart_config['frequency']*1000);
                                    tmp_current_class.set_interval_num(tmp_interval_num);

                                };
                                // console.log(tmp_current_class.callback);
                                if (tmp_current_class.callback != null) {
                                    tmp_current_class.callback.fire();
                                }

                                for (var i = 0; i < this.series.length; i++) {
                                    // if () {};
                                    if (tmp_chart_config['series-name___' + i] != undefined) {
                                        this.legend.allItems[i].update({name:tmp_chart_config['series-name___' + i]});
                                    };
                                };

                                // console.log(tmp_chart_config);

                                for (var i = 0; i < this.series.length; i++) {
                                    // if () {};
                                    if (tmp_chart_config[tmp_current_class.hidden_status_prefix + this.series[i].name] != undefined &&
                                        tmp_chart_config[tmp_current_class.hidden_status_prefix + this.series[i].name]) {
                                        this.series[i].hide();
                                    };
                                };
                            }
                        },
                        zoomType:'x',
                    },
                    navigator:
                    {
                    	enabled:false
                    },
                    scrollbar:
                    {
                    	enabled:false
                    },
                    legend: {
                        enabled: true,
                        align: 'center',
                        backgroundColor: '#FCFFC5',
                        y: 0,
                        shadow: true,
                        labelFormatter : function()
                        {
                            return this.name;
                        }
                    },
                    title:
                    {
                        text:null
                    },
                    rangeSelector : {
                        enabled:false
                    },
                    xAxis: {
                        type: 'datetime',
                        tickPixelInterval: 150
                    },
                    yAxis: current_yAxis,
                    plotOptions:{
                        line:{
                            turboThreshold:1000000,
                            connectNulls: true,
                            dataGrouping:
                            {
                                enabled:false
                            },
                            stickyTracking: false,
                            events:{
                                legendItemClick: function(event){
                                    // console.log(this);
                                    // console.log(tmp_current_class);
                                    var hidden_series_name = tmp_current_class.hidden_status_prefix + this.name;
                                    // console.log(hidden_series_name, this.visible);
                                    if ( this.visible ) {
                                        tmp_current_class.chart_config[hidden_series_name] = true;
                                    }
                                    else
                                    {
                                        if (tmp_current_class.chart_config[hidden_series_name] != undefined) {
                                            tmp_current_class.chart_config[hidden_series_name] = false;
                                        };
                                    }
                                    // console.log(tmp_chart_config);
                                }
                            },
                        },
                        series:{
                            stickyTracking: false,
                            events: {
                                click: function (event) {

                                    if (event.altKey || event.ctrlKey || event.shiftKey) {
                                        var series_name = this.name;
                                        var metric_name = '';
                                        var name_space = '';
                                        if (series_name.split(' ').length > 1) {
                                            for (var i = 1; i < series_name.split(' ').length; i++) {
                                                metric_name += series_name.split(' ')[i];
                                            };
                                            // var metric_name = series_name.split(' ')[1];
                                            name_space = series_name.split(' ')[0];
                                        }
                                        else
                                        {
                                            metric_name = series_name;
                                        }



                                        var current_series = this;

                                        var mytext = '<input type="text" id="series-name-input" placeholder="new metric name" value="' + metric_name + '" />';
                                        $('<div id="dialog" title="Change chart series name">'+mytext+'</div>').appendTo('body');        
                                        $("#dialog").dialog({                   
                                                width: 400,
                                                modal: true,
                                                create : function( event, ui)
                                                {
                                                    $('.ui-widget-overlay').css("z-index","2000");
                                                    $('.ui-dialog').css("z-index","2001");
                                                    $('#series-name-input').select();
                                                    $('#series-name-input').focus();
                                                },
                                                buttons: {
                                                    "Confirm": function() {
                                                      // $( this ).dialog( "close" );
                                                      // $("#dialog").remove();
                                                        var new_metric_name = $('#series-name-input').val();
                                                        if (new_metric_name.length > 0) {
                                                            var new_series_name = name_space + ' ' + new_metric_name;
                                                            current_series.name = new_series_name;
                                                            var current_index = 0;
                                                            for (var i = 0; i < current_series.chart.series.length; i++) {
                                                                if (current_series.chart.series[i] == current_series) {
                                                                    current_index = i;
                                                                }; 
                                                            }

                                                            // if(tmp_current_class.chart_config['series_name'] == undefined)
                                                            // {
                                                            //     tmp_current_class.chart_config['series_name'] = {};
                                                            // }

                                                            // tmp_current_class.chart_config['series_name'][current_index] = new_series_name ;

                                                            tmp_current_class.chart_config['series-name' + '___' + current_index] = new_series_name;
                                                            // console.log(tmp_current_class.chart_config);
                                                            // console.log(current_index);
                                                            current_series.chart.legend.allItems[current_index].update({name:new_series_name});
                                                            $("#dialog").remove();
                                                        }
                                                        else
                                                        {
                                                            alert('new series name cannot be empty');
                                                        }

                                                    },
                                                    Cancel: function() {
                                                      // $( this ).dialog( "close" );
                                                      $("#dialog").remove();
                                                    }
                                                  },
                                                close: function(event, ui) {
                                                    $("#dialog").remove();
                                                }
                                        });
                                    };
                                    // alert(this.name + ' clicked\n' + 'Alt: ' + event.altKey + '\n' + 'Control: ' + event.ctrlKey + '\n' + 'Shift: ' + event.shiftKey + '\n');
                                }
                            }
                        }
                    },
                    
                    credits:{
                        enabled:false
                    },
                    tooltip: current_tooltip,
                    series : current_series_data
                 });
        }
        // var series_name = [];
        //console.log(series_info[sortId]);
        var current_class = this;
        var option = {
        	url: '/chart/init/', 
        	type: 'POST',
        	data: JSON.stringify({'selected_metrics':this.selected_metrics,'chart_config':this.chart_config}),  
        	dataType: 'json', 
        	contentType : 'application/json', 
        	success: function (data) {

                // console.log(data);
        		if( ! data.init_result_bool )
        		{
        			$(data['chart_config']['container_selector']).empty();
                    result_str = '';
                    result_str += '<div class="alert alert-' + 'danger' + '">';
                    result_str += '<button type="button" class="close" data-dismiss="alert">&times;</button>';
                    result_str += data.info;
                    result_str += '</div>';
                    $(data['chart_config']['container_selector']).append(result_str);
        		}
        		else
        		{
                    // console.log(data.info);
        			var current_series_data = data.init_result;

                    var unitname_format_map = {};
                    unitname_format_map['Count'] = '';
                    unitname_format_map['USD'] = '$';
                    unitname_format_map['Percent'] = '%';
                    unitname_format_map['Byte'] = 'B';
                    unitname_format_map['Process Counts'] = '';
                    unitname_format_map['Second'] = 's';
                    unitname_format_map['Bps'] = 'bps';
                    unitname_format_map['Millsecond'] = 'ms';
                    unitname_format_map['unknown'] = '';

                    


                    // var unit_dict = {};
                    var axis_index = 0;


                    var tmp_yAxis = [];
                    var opposite_flag = false;

                    for( var i = 0 ; i  < data.init_result.length ; i ++)
                    {
                        var current_axis = {};
                        // current_axis[]
                        var tmp_min = 0;

                        current_axis = {
                            min : tmp_min ,
                            labels : 
                            {
                                // format : '{value}' + unitname_format_map[data.init_result[i].unit_name],
                                style : {
                                    color: Highcharts.getOptions().colors[i]
                                }
                            },
                            title : 
                            {
                                text : data.init_result[i].unit_name,
                                style: {
                                    color: Highcharts.getOptions().colors[i] 
                                }
                            },
                            opposite : opposite_flag
                        }
                        tmp_yAxis.push(current_axis);

                        opposite_flag = ! opposite_flag;
                    }

                    if (data['chart_config']['shared_yaxis'] == undefined || data['chart_config']['shared_yaxis']) {
                        tmp_yAxis = {
                            min : 0
                        }
                    }

                    var tmp_tooltip = {
                        crosshairs:[true,true],
                        valueDecimals: 2,
                        shared:false,
                        formatter: function () {
                            var s = 'Value:<b>' + parseFloat(this.y).toFixed(2) + '</b><br/>';
                            s += 'Time:<b>' + Highcharts.dateFormat('%Y/%m/%d %H:%M', this.x) + '</b><br/>';
                            var series_name = this.series.name;
                            var metric_name = '';
                            var name_space = '';
                            if (series_name.split(' ').length > 1) {
                                for (var i = 1; i < series_name.split(' ').length; i++) {
                                    metric_name += series_name.split(' ')[i] + ' ';
                                };
                                // var metric_name = series_name.split(' ')[1];
                                name_space = series_name.split(' ')[0];
                            }
                            else
                            {
                                metric_name = series_name;
                            }
                            
                            s += 'Metric Name:<b>' + metric_name + '</b><br/>';
                            s += 'Namespace:<b>' + name_space + '</b><br/>';
                            // var s = '<b>' + Highcharts.dateFormat('%A, %b %e, %Y', this.x) + '</b>';

                            // $.each(this.points, function () {
                            //     s += '<br/>1 USD = ' + this.y + ' EUR';
                            // });

                            return s;
                        },
                        snap: 1/1
                    }

                    current_class.clear_chart();
                    create_highstock_chart(current_series_data,current_class,tmp_yAxis,tmp_tooltip,data['chart_config']);

                    if (data.info.indexOf('successfully') <= 0 ) {
                        current_class.add_load_chart_message(data.info,'info');
                    };
                        // console.log('info');
        		}
        	}  
        };  
        if (this.init_ajax != null) {
            this.init_ajax.abort();
        };
        this.init_ajax = $.ajax(option);
    }

    this.add_load_chart_message = function(message,type)
    {

        $("#info-dialog").remove();
        $('<div id="info-dialog" title="load chart info"><p>' + message + '</p></div>').appendTo('body');
        $("#info-dialog").dialog({ 
            width: 400,
            create : function( event, ui)
            {
                $('.ui-widget-overlay').css("z-index","2000");
                $('.ui-dialog').css("z-index","2001");
            },
            close: function(event, ui) {
                $("#info-dialog").remove();
            }
        });

        setTimeout(function(){
            $("#info-dialog").dialog('close');
        },4000);
    }

    this.clear_interval = function()
    {
        // if (this.interval_number != undefined) {
        clearInterval(this.interval_number);
        // }
    }

    this.update = function()
    {
        var current_class = this;
        // console.log(this);
    	var option = {  
    		url: '/chart/update/',  
    		type: 'POST',  
    		data: JSON.stringify({'selected_metrics':this.selected_metrics,'chart_config':this.chart_config}),  
    		dataType: 'json', 
    		contentType : 'application/json', 
    		success: function (data) {
    			// console.log(data);
    			if (data.update_result_bool) {
    				for (var i = 0; i < data.update_result.length; i++) {
    					// console.log(data.update_result[i]);
                        // if (data.update_result[i][1] != null) 
                        {
                            current_class.mychart.series[i].addPoint(data.update_result[i],false,true);
                        }
    					
    					// data.update_result[i]
    				};
    				 current_class.mychart.redraw();
    			}
                else
                {
                    console.log(data.info);
                }
            }  
        };  

        if (this.update_ajax != null) {
            this.update_ajax;
        };
        this.update_ajax = $.ajax(option);
    }

    this.get_time_range = function()
    {
        result = null;
        if (this.mychart != undefined) {
            // console.log();
            result = this.mychart.xAxis[0].getExtremes();
        }
        return result ;
    }

    

}