function create_chart(container,sortId,series_info,chart_title,is_init_empty,time_frequency,callbacks,max_display_count,mychart,si,last_update_time) {

    function init_clear(container_selector,sortId)
    {
        $(container_selector).empty();
        if (mychart[sortId] != undefined) {
            mychart[sortId].destroy();
            mychart[sortId] = null;
        };

        if (si[0] != undefined) {
            clearInterval(si[0]);
                // console.log("cleared");
        };
    }

    function add_window_init(container_selector,sortId)
    {
        // console.log("add_window_init");
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
        init_clear(container_selector,sortId);
    }

    

    function add_window(container,sortId,chart_title)
    {
        container_selector = 'div[container="' + container + '"][sortId=' + sortId + ']';

        add_window_init(container_selector,sortId);
         $(container_selector).append('<button class="btn btn-lg btn-info"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</button>');
        var series_for_current_window = [];
        var series_counter = 0 ;
        // console.log(chart_title);
        create_highstock_chart = function(container_selector,sortId,y_title){
                 $(container_selector).highcharts('StockChart',{
                    chart:{
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                mychart[sortId] = this;
                                si[0] = setInterval(update,time_frequency*1000);
                            }
                        }
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
                        // selected : 1,
                        inputEnabled: $(container_selector).width() > 480,
                        selected : 1,
                        buttons: [
                            {
                                type:'hour',
                                count:1,
                                text:'1h'   
                            },
                            {
                                type:'hour',
                                count:6,
                                text:'6h'   
                            },
                            {
                                type: 'day',
                                count: 1,
                                text: '1d'
                            }, 
                            {
                                type: 'all',
                                text: 'All'
                            }
                        ]
                    },
                    title : {
                        text : chart_title
                    },
                    xAxis: {
                        type: 'datetime',
                        tickPixelInterval: 150
                    },
                    yAxis: {
                        title: {
                            text: y_title
                        },
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
                            connectNulls: true
                        }
                    },
                    credits:{
                        enabled:false
                    },

                    tooltip: {
                        crosshairs:[true,true],
                        valueDecimals: 2
                    },

                    series : series_for_current_window

                 });
                
                if (si[1] != undefined) {
                    callbacks.add(si[1]);
                    // console.log("children",callbacks.has(si[1]));
                    callbacks.fire(sortId);
                };
        }

        var series_name = [];
        var option = {  
               url: '/chart/init/',  
               type: 'POST',  
               data: JSON.stringify({'current_series_info':series_info[sortId],'time_frequency':time_frequency}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    if (data == 0) {
                        $(container_selector).empty();
                        $(container_selector).append('<button class="btn btn-lg btn-info">No Monitor data to display</button>');
                    }
                    else
                    {
                        series_for_current_window = data.data;
                        y_title = data.y_title;
                        create_highstock_chart(container_selector,sortId,y_title);
                    }
                }  
        };  
        $.ajax(option);
    }

    function update()
    {
        var now = (new Date()).getTime();
        time_till = now;
        time_till = Math.floor(now/1000);
        var option = {  
               url: '/chart/update/',  
               type: 'POST',  
               data: JSON.stringify({'series_info':series_info,'time_frequency':time_frequency,'time_till':time_till}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    // console.log(data);
                    for (var ci = 0; ci < data.length; ci ++) {
                        for (var si = 0; si < data[ci].length; si++) {
                            series = mychart[ci].series[si].addPoint(data[ci][si],false,true);
                        };
                    };
                    for (var i = 0; i < data.length; i++) {
                        if (mychart[i] != undefined )
                        {
                            mychart[i].redraw();
                        }
                    };
                }  
        };  
        $.ajax(option);
    }


    callbacks = $.Callbacks();
    // console.log(si);
    add_window(container,sortId,chart_title);
    
}



