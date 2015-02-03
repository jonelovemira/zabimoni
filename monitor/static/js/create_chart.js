function create_chart(container,sortId,series_info,chart_title,series_index,time_frequency,callbacks,max_display_count,mychart,si,series_time_frequency) {

    function init_clear(container_selector,sortId)
    {
        $(container_selector).empty();
        if (mychart[sortId] != undefined) {
            mychart[sortId].destroy();
            mychart[sortId] = null;
        };
        if (si[0] != undefined) {
            clearInterval(si[0]);
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

    $(document).on('click','button.change',function(){
        value = parseInt($('input[name=newfrequency]').val());
        // alert(value);
        // console.log(time_frequency);
        // console.log(si[0]);
        if (si[0] != undefined && value >= 10) {
            // console.log(mychart[sortId]);
            clearInterval(si[0]);
            time_frequency = value;
            si[0] = setInterval(update,value*1000);
            if (si.length == 1) {
                si.push(value);
            }else
            {
                si[1] = value;
            }
            // mychart[sortId].options.exporting.buttons.customButton.attr({text : "frequency:" + value});
            //console.log(mychart[sortId].options.exporting.buttons.customButton);
            // button = mychart[sortId].options.exporting.buttons.customButton;
            // console.log(button);
            // button.text = "frequency:" + value;
            // mychart[sortId].redraw()
            // button.attr({'text':'nihao'});
        };
        $('#changefrequency').modal('hide');
    });
    

    function add_window(container,sortId,chart_title)
    {
        container_selector = 'div[container="' + container + '"][sortId=' + sortId + ']';
        add_window_init(container_selector,sortId);
        $(container_selector).append('<button class="btn btn-lg btn-info"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</button>');
        var series_for_current_window = [];
        // console.log(chart_title);
        create_highstock_chart = function(container_selector,sortId,y_title,current_series_data){
                 $(container_selector).highcharts('StockChart',{
                    chart:{
                        ignoredHiddenSeries:false,
                        events : {
                            load : function(){
                                mychart[sortId] = this;
                                if (si[0] == undefined) {
                                    si[0] = setInterval(update,time_frequency*1000);
                                };
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
                    exporting:{
                        buttons:{
                            customButton:{
                                x:-62,
                                onclick:function(){
                                    $('#changefrequency').modal({
                                        keyboard: false
                                    });
                                    $('#changefrequency').modal('show');
                                },
                                text: 'frequency:' + time_frequency
                            },
                            customButton2:{
                                x:-180,
                                text: 'function: avg',
                                menuItems: [{
                                    text: 'count',
                                    // onclick: function () {
                                    //     alert("count");
                                    // }
                                }, {
                                    text: 'avg',
                                    // onclick: function () {
                                    //     alert("avg");
                                    // }
                                },{
                                    text: 'max',
                                    // onclick: function () {
                                    //     alert("min");
                                    // }
                                },{
                                    text: 'min',
                                    // onclick: function () {
                                    //     alert("max");
                                    // },
                                }]
                            }
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
                                type:'minute',
                                count:30,
                                text:'30m'   
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
               url: '/chart/init2/',  
               type: 'POST',  
               data: JSON.stringify({'current_series_info':series_info[sortId],'time_frequency':time_frequency,'sortId':sortId}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    current_sortId = data.sortId;
                    current_container_selector = 'div[container="' + container + '"][sortId=' + current_sortId + ']';
                    if (data.data == 0) {
                        console.log(current_sortId);
                        init_clear(current_container_selector,current_sortId)
                        $(current_container_selector).append('<button class="btn btn-lg btn-warn">No Monitor data to display</button>');
                        // console.log("clear");
                    }
                    else
                    {
                        current_series_data = data.data;
                        y_title = data.y_title;
                        create_highstock_chart(current_container_selector,current_sortId,y_title,current_series_data);
                        $(current_container_selector).after('<button class="btn btn-info morehistory" sortId=' + current_sortId + ' style="margin-bottom:0px;margin-top:3px">More history about this chart>></button>');
                    }
                    $('button.itemtype').removeAttr("disabled");
                }  
        };  
        $.ajax(option);
    }

    function update()
    {
        // console.log(mychart[sortId].series);
        navigator_series_index = [];
        for (var ci = 0; ci < series_info.length;ci ++) {
            var tmp;
            navigator_series_index.push(tmp);
            if (mychart[ci] != undefined) {
                for (var si = 0; si < mychart[ci].series.length; si++) {
                    if(mychart[ci].series[si].name == 'Navigator')
                    {
                        navigator_series_index[ci] = si;
                    }
                };
            };
        };
        // for (var i = mychart[sortId].series.length - 1; i >= 0; i--) {
        //     if(mychart[sortId].series[i].name == 'Navigator')
        //     {
        //         navigator_series_index = i;
        //         break;
        //     }
        // };
        var now = (new Date()).getTime();
        time_till = now;
        time_till = Math.floor(now/1000);
        var option = {  
               url: '/chart/update2/',  
               type: 'POST',  
               data: JSON.stringify({'series_info':series_info,'time_frequency':time_frequency,'time_till':time_till}),  
               dataType: 'json', 
               contentType : 'application/json', 
               success: function (data) {
                    for (var ci = 0; ci < data.length; ci ++) {
                        for (var si = 0; si < data[ci].length; si++) {
                            if (si >= navigator_series_index[ci] ) {
                                series = mychart[ci].series[si + 1].addPoint(data[ci][si],false,true);
                            }
                            else
                            {
                                series = mychart[ci].series[si].addPoint(data[ci][si],false,true);
                            }
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
    // base_series_num = 0;
    // console.log(si);
    if (mychart[sortId] == undefined) {
        add_window(container,sortId,chart_title);
    }
    else
    {
        // console("another init");
        // console.log(series_info);
        var series_info_tmp = []
        series_info_tmp.push(series_info[sortId][series_index])
        var option = {  
            url: '/chart/init/',  
            type: 'POST',  
            data: JSON.stringify({'current_series_info':series_info_tmp,'time_frequency':series_time_frequency,'sortId':sortId}),  
            dataType: 'json', 
            contentType : 'application/json', 
            success: function (data) {
                if (data.data != 0) {
                    clearInterval(si[0]);
                    mychart[sortId].addSeries(data.data[0])
                    //console.log(data)
                    // console.log(mychart[sortId]);
                    current_title = mychart[sortId].yAxis[0].axisTitle.textStr;
                    current_title += ',' + data.y_title; 
                    //console.log(current_title);
                    // console.log(mychart[sortId].yAxis.title);
                    mychart[sortId].yAxis[0].axisTitle.attr({text: current_title });
                    si[0] = setInterval(update,time_frequency*1000);
                    $('button.itemtype').removeAttr("disabled");
                }   
            }  
        };  
        $.ajax(option);
    }
    
    
}



