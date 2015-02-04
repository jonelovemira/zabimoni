function chart()
{

	var mychart;
	var interval_number;
	var selected_metrics;
	var chart_config;

	this.set_selected_metrics = function(new_selected_metrics)
	{
		selected_metrics = new_selected_metrics;
	}

	this.set_chart_config = function(new_chart_config)
	{
		chart_config = new_chart_config;
	}

	this.clear_chart = function()
	{
		if (chart_config != undefined) {
			$(chart_config['container_selector']).empty();
		};
        if (mychart != undefined) {
            mychart.destroy();
            mychart = null;
        };
        if (interval_number != undefined) {
            clearInterval(interval_number);
        }
	}

	this.set_highchart = function()
	{
		Highcharts.setOptions({
            global: {
                useUTC: chart_config['use_utc']
            }
        });
	}

	// clear_chart();
	// set_highchart();

	this.create_chart = function()
    {
        // container_selector = 'div[container="' + container + '"][sortId=' + sortId + ']';
        // add_window_init(container_selector,sortId);
        $(chart_config['container_selector']).append('<button class="btn btn-lg btn-info"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</button>');
        var series_for_current_window = [];
        // console.log(chart_title);
        create_highstock_chart = function(current_series_data){
                 // $(chart_config['container_selector']).highcharts({
                 $(chart_config['container_selector']).highcharts('StockChart',{
                    chart:{
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                mychart = this;
                                if (chart_config['update_flag']) {
                                    interval_number = setInterval(update,chart_config['frequency']*1000);
                                };
                            }
                        }
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
                        borderColor: 'black',
                        borderWidth: 2,
                        layout: 'vertical',
                        verticalAlign: 'bottom',
                        y: 0,
                        shadow: true,
                        labelFormatter : function()
                        {
                            return this.name;
                        }
                    },
                    rangeSelector : {
                        enabled:false
                    },
                    xAxis: {
                        type: 'datetime',
                        tickPixelInterval: 150
                    },
                    yAxis: {
                        min : 0,
                        startOnTick :false,
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    plotOptions:{
                        line:{
                            turboThreshold:1000000,
                            connectNulls: true,
                            dataGrouping:
                            {
                                enabled:false
                            }
                        }
                    },
                    credits:{
                        enabled:false
                    },
                    tooltip: {
                        crosshairs:[true,true],
                        valueDecimals: 2
                    },
                    series : current_series_data

                 });
        }
        var series_name = [];
        //console.log(series_info[sortId]);
        var option = {
        	url: '/chart/init/', 
        	type: 'POST',  
        	data: JSON.stringify({'selected_metrics':selected_metrics,'chart_config':chart_config}),  
        	dataType: 'json', 
        	contentType : 'application/json', 
        	success: function (data) {

                // console.log(data);
        		if( ! data.init_result_bool )
        		{
        			$(chart_config['container_selector']).append('<button class="btn btn-lg btn-warn">No Monitor data to display</button>');
                    console.log(data.info);
        		}
        		else
        		{
        			current_series_data = data.init_result;
        			create_highstock_chart(current_series_data);
                    // $(window).trigger('resize');
        		}
        	}  
        };  
        $.ajax(option);
    }

    function update()
    {
    	var option = {  
    		url: '/chart/update/',  
    		type: 'POST',  
    		data: JSON.stringify({'selected_metrics':selected_metrics,'chart_config':chart_config}),  
    		dataType: 'json', 
    		contentType : 'application/json', 
    		success: function (data) {
    			console.log(data);
    			if (data.update_result_bool) {
    				for (var i = 0; i < data.update_result.length; i++) {
    					console.log(data.update_result[i]);
                        if (data.update_result[i][1] != null) {
                            mychart.series[i].addPoint(data.update_result[i],false,true);
                        }
    					
    					// data.update_result[i]
    				};
    				 mychart.redraw();
    			};

                    // for (var ci = 0; ci < data.length; ci ++) {
                    //     for (var si = 0; si < data[ci].length; si++) {
                    //         if (si >= navigator_series_index[ci] ) {
                    //             series = mychart[ci].series[si + 1].addPoint(data[ci][si],false,true);
                    //         }
                    //         else
                    //         {
                    //             series = mychart[ci].series[si].addPoint(data[ci][si],false,true);
                    //         }
                    //     };
                    // };
                    // for (var i = 0; i < data.length; i++) {
                    //     if (mychart[i] != undefined )
                    //     {
                    //         mychart[i].redraw();
                    //     }
                    // };
            }  
        };  
        $.ajax(option);
    }

    this.get_time_range = function()
    {
        result = null;
        if (mychart != undefined) {
            // console.log();
            result = mychart.xAxis[0].getExtremes();
        }
        return result ;
    }
}