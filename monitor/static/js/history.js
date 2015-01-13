function history(container,current_series_info,chart_title,time_frequency,max_display_count,mychart) {

    function init_clear(container_selector)
    {
        $(container_selector).empty();
        if (mychart != undefined) {
            mychart.destroy();
            mychart = null;
        };
    }

    function add_window_init(container_selector)
    {
        // console.log("add_window_init");
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
        init_clear(container_selector);
    }


    function afterSetExtremes(e) {

        var chart = mychart;

        chart.showLoading('Loading data from server...');

        // console.log(current_series_info,e.max,e.min);
        var option = {  
               url: '/chart/interval/',  
               type: 'POST',  
               data: JSON.stringify({'current_series_info':current_series_info,'time_till':Math.round(e.max/1000),'time_since':Math.round(e.min/1000)}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    // console.log(data.data);
                    for (var i = 0; i < data.data.length; i++) {
                        chart.series[i].setData(data.data[i].data);
                    }
                    chart.hideLoading();
                }  
        };  
        $.ajax(option);

        // $.getJSON('http://www.highcharts.com/samples/data/from-sql.php?start=' + Math.round(e.min) +
        //         '&end=' + Math.round(e.max) + '&callback=?', function (data) {

        //         chart.series[0].setData(data);
        //         chart.hideLoading();
        //     });
    }

    

    function add_history_window(container,chart_title)
    {
        // width = $('div[udf=modal-history]').width()
        // console.log("width",width);
        container_selector = 'div[container="' + container + '"]';
        add_window_init(container_selector);
        $(container_selector).append('<button class="btn btn-lg btn-info"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</button>');
        var series_for_current_window = [];
        var series_counter = 0 ;
        // console.log(chart_title);
        create_highstock_chart = function(container_selector,y_title){
                 $(container_selector).highcharts('StockChart',{
                    chart:{
                        zoomType:'x',
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                mychart = this;
                            }
                        },
                        // width: $('div[udf="modal-history"]').width()
                        // width: 868
                    },
                    navigator : {
                        adaptToUpdatedData: false,
                        series : {
                            data: series_for_current_window[0].data
                        }
                    },
                    scrollbar: {
                        liveRedraw: false
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
                        selected : 3,
                        buttons: [
                            {
                                type:'hour',
                                count:1,
                                text:'1h'   
                            },
                            {
                                type:'hour',
                                count:2,
                                text:'2h'   
                            },
                            {
                                type:'hour',
                                count:6,
                                text:'6h'   
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
                        events : {
                            afterSetExtremes : afterSetExtremes
                        },
                        minRange: 9000 * 1000
                    },
                    yAxis: {
                        // title: {
                        //     text: y_title
                        // },
                        // min : 0,
                        // startOnTick :false,
                        // plotLines: [{
                        //     value: 0,
                        //     width: 1,
                        //     color: '#808080'
                        // }],
                        floor:0
                    },
                    plotOptions:{
                        line:{
                            // turboThreshold:1000000,
                            connectNulls: true,
                            // dataGrouping:
                            // {
                            //     enabled:false
                            // }
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
        }

        var series_name = [];
        var option = {  
               url: '/chart/history/',  
               type: 'POST',  
               data: JSON.stringify({'current_series_info':current_series_info,'time_frequency':time_frequency}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    if (data == 0) {
                        init_clear(container_selector,sortId)
                        $(container_selector).append('<button class="btn btn-lg btn-info">No Monitor data to display</button>');
                        // console.log("clear");
                    }
                    else
                    {
                        // console.log(data);
                        series_for_current_window = data.data;
                        y_title = data.y_title;
                        create_highstock_chart(container_selector,y_title);
                        $(window).trigger('resize');
                    }
                }  
        };  
        $.ajax(option);
    }

    if (mychart == undefined) {
        add_history_window(container,chart_title);
    }
}



