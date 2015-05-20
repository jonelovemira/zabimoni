function create_report(container,sortId,series_info,time_frequency,mychart,time_since,time_till,functiontype) {

    function init_clear(container_selector,sortId)
    {
        $(container_selector).empty();
        if (mychart[sortId] != undefined) {
            mychart[sortId].destroy();
            mychart[sortId] = null;
        };
    }

    function add_window_init(container_selector,sortId)
    {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
        init_clear(container_selector,sortId);
    }

    function add_window(container,sortId,chart_title)
    {
        container_selector = 'div[class="' + container + '"][sortId=' + sortId + ']';
        add_window_init(container_selector,sortId);
        var series_for_current_window = [];
        var series_counter = 0 ;
        create_highstock_chart = function(container_selector,sortId){
                 $(container_selector).highcharts('StockChart',{
                    chart:{
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                mychart[sortId] = this;
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
                        selected : 0,
                        buttons: [
                            {
                                type:'minute',
                                count:10,
                                text:'10m'
                            },
                            {
                                type:'hour',
                                count:1,
                                text:'1h'   
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
                            text: 'Value'
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
                            turboThreshold:1000000
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
               url: '/chart/report/init2/',  
               type: 'POST',  
               data: JSON.stringify({'current_series_info':series_info[sortId],'functiontype':functiontype,'time_frequency':time_frequency,'time_since':time_since,'time_till':time_till}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    series_for_current_window = data.data;
                    create_highstock_chart(container_selector,sortId);
                }  
        };  
        $.ajax(option);
    }

    add_window(container,sortId);
    
}