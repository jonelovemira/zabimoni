function window_base()
{
    // sidebar a href
    sidebar_page_class = 'sidebar-page';
    sidebar_page_selector = 'a.' + sidebar_page_class;
    sidebar_option_class = 'sidebar-option';
    sidebar_option_selector = 'a.' +  sidebar_option_class;
    sidebar_page_li_selector = 'li.' + sidebar_page_class;

    // dashboard main 
    dashboard_main_class = 'dashboard-main';
    dashboard_main_selector = 'div.' + dashboard_main_class;




    main_board_selector = "div.indexmain";
    selected_metric_li_class = 'selected-metrics';
    selected_metric_li_selector = 'li.' + selected_metric_li_class;

    // top category config
    top_category_main_class = 'top-category-main';
    top_category_main_selector = 'div.' + top_category_main_class;
    top_category_selector = "div.top-category";
    browsemetric_button_str = "<button class='btn btn-primary form-control browsemetric' type='button'>Browse Metrics</button>"
    browsemetric_button_selector = "button.browsemetric";
    search_input_str = '<input type=text class="form-control search" placeholder="input Metrics Name"/>';
    search_input_selector = "input.search";
    default_selected = 'Browse Metrics';
    default_searched_value = '';
    option_select_selector = '#metricoptions';

    //search result panel
    search_result_main_class = "search-result-main"; 
    search_result_main_selector = 'div.' + search_result_main_class; 
    search_result_panel_class = "search-result-panel-test";
    search_result_panel_selector = "div." + search_result_panel_class;

    // basic metrics panel
    basicmetrics_panel_class = "basicmetrics-panel";
    basicmetrics_panel_selector = "div." + basicmetrics_panel_class;

    //pre-saved search
    pre_saved_search_calss = 'pre-saved-search';
    pre_saved_search_selector = 'div.' + pre_saved_search_calss;

    //message 
    message_class = 'query-result-message';
    message_selector = 'div.' + message_class;

    // selected metric action
    select_action_class = 'select-action';
    select_action_selector = 'div.' + select_action_class;

    // basic metrics levels
    basic_metrics_first_class = 'basic-metrics-1';
    basic_metrics_first_selector = 'a.' + basic_metrics_first_class;

    basic_metrics_second_class = 'basic-metrics-2';
    basic_metrics_second_selector = 'a.' + basic_metrics_second_class;

    // search result table
    search_result_div_class = 'search-result-div';
    search_result_div_selector = 'div.' + search_result_div_class;
    search_result_table_class = 'search-result-table';
    search_result_table_selector = 'table.' + search_result_table_class;
    search_result_table_title_class = 'search-result-table-title';
    option_title_spliter = '>';

    //metric select input
    select_metric_input_class = 'select-metric-input';
    select_metric_input_selector = 'input.' + select_metric_input_class;

    //chart main panel
    chart_div_class = 'chart';
    chart_div_selector = 'div.' + chart_div_class; 
    chart_main_div_class = 'chart-main';
    chart_main_div_selectoer = 'div.' + chart_main_div_class;
    chart_main_header_div_class = 'chart-main-header-config';
    chart_main_header_div_selector = 'div.' + chart_main_header_div_class;
    chart_main_pagination_class = 'chart-main-pagination';
    chart_main_pagination_selector = 'div.' + chart_main_pagination_class;
    chart_main_display_container_class = 'chart-main-display-container';
    chart_main_display_container_selector = 'div.' + chart_main_display_container_class;
    chart_sidebar_config_class = 'chart-sidebar-config';
    chart_sidebar_config_selector = 'div.' + chart_sidebar_config_class;

    //chart config
    function_type_class = 'function-type';
    function_type_selector = 'select.' + function_type_class;
    frequency_setting_class = 'frequency-setting';
    frequency_setting_selector = 'select.' + frequency_setting_class;
    utc_radio_class = 'utc-choose';
    utc_radio_selector = 'input.' + utc_radio_class;
    from_time_class = 'from-time';
    from_time_selector = 'div.' + from_time_class;
    to_time_class = 'to-time';
    to_time_selector = 'div.' + to_time_class;
    zoom_type = 'zoom-type';
    zoom_type_selector = 'a.' + zoom_type;
    update_graph_button_class = 'update-graph';
    update_graph_button_selector = 'a.' + update_graph_button_class ;
    sidebar_config_message_class = 'sidebar-config-message';
    sidebar_config_message_selector = 'div.' + sidebar_config_message_class;
    refresh_icon_class = 'refresh-chart';
    refresh_icon_selector = 'a.' + refresh_icon_class;
    chart_left_icon_class = 'chart-left';
    chart_left_icon_selector = 'a.' + chart_left_icon_class ;
    chart_right_icon_class = 'chart-right';
    chart_right_icon_selector = 'a.' + chart_right_icon_class ;





    // flag for if browse or search
    default_browse_flag = false;
    // default_update_search_table = true;


    // global variables
    var selected_metric_result = {};

    //chart configurations
    var chart_config = {};
    var display_chart = new chart();

    set_default_chart_config();

    function set_default_chart_config()
    {
        chart_config['frequency'] = 60;
        chart_config['function_type'] = 'Average';
        chart_config['container_class'] = chart_main_display_container_class;
        chart_config['container_selector'] = chart_main_display_container_selector;
        chart_config['use_utc'] = false;
        chart_config['init_time_length'] = 60 * 60;
        chart_config['update_flag'] = true;
    }



    function arr_equal(compareFrom,compareTo) {
        if (!compareTo || compareFrom.length != compareTo.length) {
            return false;
        }
        for (var i = 0; i < compareFrom.length; ++i) {
            if (compareFrom[i] != compareTo[i]) {
                return false;
            }
        }
        return true;
    };


	$(sidebar_page_li_selector).click(function()
	{
        target = $(this);
		make_active(sidebar_page_li_selector,target);
	});

    $(document).on('keypress',search_input_selector,function(event)
    {
        if ( event.which == 13) {
            option = $(option_select_selector).val();
            search_value = $(this).val();
            option = option || default_selected;
            search_value = search_value || default_searched_value;
            metric_render_main(option,search_value);
        };
    });

    $(document).on('change',option_select_selector,function()
    {
        option = $(this).val();
        metric_render_main(option);
    });

    $(document).on('click',sidebar_page_selector,function()
    {
        clear_main();
        page = $(this).attr("page");
        option = $(this).attr("option");
        hidden_chart();
        // console.log(page,option);
        if (page != undefined) {
            render_main_by_page(page);
        }
        else
        {
            if (option != undefined) {
                metric_render_main(option);
            };
        }
    });

    $(document).on('click',sidebar_option_selector,function()
    {
        clear_main();
        page = $(this).attr("page");
        option = $(this).attr("option");
        hidden_chart();
        // console.log(page,option);
        if (page != undefined) {
            render_main_by_page(page);
        }
        else
        {
            if (option != undefined) {
                metric_render_main(option);
            };
        }
    })

    // $('a[locate="main-sidebar"]').click(function()
    // {
    //     clear_main();
    //     page = $(this).attr("page");
    //     option = $(this).attr("option");
    //     hidden_chart();
    //     // console.log(page,option);
    //     if (page != undefined) {
    //         render_main_by_page(page);
    //     }
    //     else
    //     {
    //         if (option != undefined) {
    //             metric_render_main(option);
    //         };
    //     }
        
    //     // return false;
    // });

    $(document).on('click',browsemetric_button_selector,function()
    {
        make_active('li',$('a[page=metric]').parent());
        metric_render_main('Browse Metrics',0,true);
    });

    $(document).on('click',basic_metrics_first_selector,function()
    {
        option = $(this).text();
        metric_render_main(option);
    });

    $(document).on('click',basic_metrics_second_selector,function()
    {
        option = $(this).closest('div').find(basic_metrics_first_selector)[0].text;
        // console.log($(this).closest('div'));
        search_value = $(this).text();
        metric_render_main(option,search_value);
    });

    $(document).on('click',select_metric_input_selector,function()
    {
        title_text = null;
        $(this).closest('div').find('.' + search_result_table_title_class).each(function(i,d)
        {
            title_text = $(this).text();
        });

        option_title = title_text.split(option_title_spliter);
        option = option_title[0];
        table_title = option_title[1];

        // console.log(option,table_title);


        table_head = [];
        $(this).closest('table').find('th').each(function(i,d)
        {
            // console.log($(this).text().length);
            if ($(this).text().length > 0) {
                table_head.push($(this).text());
            };
        });

        td_content = [];
        $(this).closest('tr').find('td').each(function(i,d)
        {
            if ($(this).text().length > 0) {
                td_content.push($(this).text());
            };
        });

        // console.log(table_head,td_content);

        metrics_checkbox_result = $(this).prop("checked");

        select_metric_change(option,table_title,table_head,td_content,metrics_checkbox_result);
    });

    $(document).on('click',selected_metric_li_selector,function(event)
    {
        clear_main();
        add_top_category('All','');
        add_search_result_panel();
        add_chart_main_panel();
        show_chart();
        for (var option in selected_metric_result)
        {
            render_search_result_to_table(option,selected_metric_result[option]);
        }

    });


    // function_type_selector,frequency_setting_selector,update_graph_button_selector,zoom_type_selector

    $(document).on('change',function_type_selector,function()
    {
        // console.log($(this).val());
        var function_type = $(this).val();
        chart_config['function_type'] = function_type;
        chart_update();
    });



    $(document).on('change',frequency_setting_selector,function()
    {
        var frequency = $(this).val();
        chart_config['frequency'] = parseInt(frequency);
        chart_update();
    });

    $(document).on('click',zoom_type_selector,function()
    {
        var init_time_length = $(this).attr("value");
        chart_config['init_time_length'] = parseInt(init_time_length);
        // console.log(chart_config['to_clock']);
        if (chart_config['to_clock'] == undefined) {
            var now = (new Date()).getTime();
            chart_config['to_clock'] = now / 1000;
            chart_config['from_clock'] = chart_config['to_clock'] - init_time_length;
            set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
            set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
        }
        else
        {
            if (chart_config['to_clock'] > init_time_length) {
                chart_config['from_clock'] = chart_config['to_clock'] - init_time_length;
                set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
                set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
            };
        }
        
        // console.log(init_time_length);
        chart_update();
    });

    $(document).on('change',utc_radio_selector,function()
    {
        var tmp_val = $(this).attr("value");
        if(parseInt(tmp_val) == 1)
        {
            use_utc = true;
        }
        else
        {
            use_utc = false;
        }
        chart_config['use_utc'] = use_utc;
        chart_update();
    });




    $(document).on('click',update_graph_button_selector,function()
    {
        // console.log("update graph");

        if (chart_config['from_clock'] == undefined || chart_config['to_clock'] == undefined) {

            add_message_2_sidebar_config_message('FROM or TO is empty','danger');
        }
        else
        {
            
            if (chart_config['to_clock'] <= chart_config['from_clock']) {
                add_message_2_sidebar_config_message('FROM time is less or equal than TO time','danger');
            }
            else
            {
                chart_config['update_flag'] = false;
                chart_config['use_utc'] = use_utc;
                chart_update();
            }
        }
        
    });

    $(document).on('click',refresh_icon_selector,function()
    {
        // chart_config = {};
        // set_default_chart_config();

        var function_type = $(function_type_selector).val();
        var frequency = $(frequency_setting_selector).val();
        // console.log(function_type,frequency);
        // function_type_selector,frequency_setting_selector;
        chart_config['update_flag'] = true;
        chart_config['function_type'] = function_type;
        chart_config['frequency'] = parseInt(frequency);
        chart_update();
    });

    $(document).on('click',chart_right_icon_selector,function()
    {
        chart_config['update_flag'] = false;
        var time_range = display_chart.get_time_range();
        if (time_range != null && time_range != undefined) {
            var from_in_ms = parseInt(time_range.dataMin);
            var to_in_ms = parseInt(time_range.dataMax);
            var new_from = to_in_ms;
            var new_to = to_in_ms + (to_in_ms - from_in_ms);

            chart_config['from_clock'] = new_from / 1000 + 60;
            chart_config['to_clock'] = new_to / 1000 + 120;

            
            chart_update();

        }
        else
        {
            var now = (new Date()).getTime() / 1000 ;
            // console.log(now);
            chart_config['from_clock'] = now  - 3600;
            chart_config['to_clock'] = now  ;
        }

        set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
        set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
        // else
        // {
        //     chart_config['from_clock'] = (new Date()).getTime();
        // }
    });

    $(document).on('click',chart_left_icon_selector,function()
    {
        chart_config['update_flag'] = false;
        var time_range = display_chart.get_time_range();
        if (time_range != null && time_range != undefined) {
            var from_in_ms = parseInt(time_range.dataMin);
            var to_in_ms = parseInt(time_range.dataMax);
            var new_from = from_in_ms - (to_in_ms - from_in_ms);
            var new_to = from_in_ms ;

            chart_config['from_clock'] = new_from / 1000 - 60;
            chart_config['to_clock'] = new_to / 1000 ;
            chart_update();

        }
        else
        {
            var now = (new Date()).getTime() / 1000 ;
            // console.log(now);
            chart_config['from_clock'] = now  - 3600;
            chart_config['to_clock'] = now  ;
        }

        set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
        set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
    });

    function set_date_to_timepicker(selector,clock)
    {
        // console.log(new Date(chart_config['from_clock'] * 1000));
        $(selector).data('DateTimePicker').setDate(new Date(clock * 1000));
    }



    function time_convert_second(use_utc,time)
    {
        var d = new Date(time);
        // console.log(d.getTime());
        // console.log(d);
        result = d.getTime()/1000;
        if ( use_utc ) 
        {
            offset_minute = -(new Date()).getTimezoneOffset();
            result = d.getTime()/1000 + offset_minute * 60 ;
        }
        return result;
    }

    function key_in_dict(key,dict)
    {
        for (var item in dict) {
            if (key == item) {
                return true;
            };
        };
        return false;
    }

    

    function update_select_badge()
    {
        total_count = 0;
        for (var option in selected_metric_result)
        {
            // console.log(selected_metric_result[option]);
            for (var table_title in selected_metric_result[option])
            {
                // console.log(table_title);
                total_count += selected_metric_result[option][table_title]['metric_result'].length;
            }
        }

        $(selected_metric_li_selector).find('span').each(function(i,d)
        {
            $(this).remove();
        });

        if (total_count > 0) {
            $(selected_metric_li_selector).append('<span class="badge">' + total_count + '</span>');
        }
        

    }

    function select_metric_change(option,table_title,table_head,td_content,metrics_checkbox_result)
    {
        
        if (metrics_checkbox_result) {

            add_metric_2_selected(option,table_title,table_head,td_content);
        }
        else
        {
            rm_metric_2_selected(option,table_title,table_head,td_content);
        }
        
        // console.log(metric_result);

        update_select_badge();


        // set_default_chart_config();
        chart_update();

    }
    
    function check_selected_metric()
    {
        var metric_count = 0;
        for (var option in selected_metric_result)
        {
            // console.log(selected_metric_result[option]);
            for (var table_title in selected_metric_result[option])
            {
                // console.log(table_title);
                metric_count += selected_metric_result[option][table_title]['metric_count'];
            }
        }
        result = false;
        if (metric_count > 0) {
            result = true;
        }
        return result;
    }

    function check_chart_config(chart_config)
    {
        chart_config['update_flag'] = chart_config['update_flag'] || true ;
        if (chart_config['update_flag']) {
            // chart_config['init_time_length'] = 3600;
            if (chart_config['init_time_length'] == undefined || chart_config['init_time_length'] == true) {
                chart_config['init_time_length'] = 3600;
            };
        }
        else
        {
            if (chart_config['to_clock'] == undefined || chart_config['to_clock'] == null) {
                var now = (new Date()).getTime() / 1000 ;
                chart_config['to_clock'] = now  ;
            }
            
            if (chart_config['from_clock'] == undefined || chart_config['from_clock'] == null) {
                chart_config['from_clock'] = chart_config['to_clock']  - 3600;
            };
        }

        if (chart_config['frequency'] == undefined || chart_config['frequency'] == null) {
            chart_config['frequency'] = 60;
        }

        if (chart_config['function_type'] == undefined || chart_config['function_type'] == null) {
            chart_config['function_type'] = 'Average';
        };
    }

    function chart_update()
    {
        check_chart_config(chart_config);
        // check_result = check_selected_metric();
        // if (check_result) {
            display_chart.set_selected_metrics(selected_metric_result);
            display_chart.set_chart_config(chart_config);
            display_chart.clear_chart();
            display_chart.set_highchart();
            display_chart.create_chart();
        // }
        // else
        // {
        //     add_message_2_sidebar_config_message('Choose at least 1 metric','danger');
        // }   
    }

    function find_metric_in_selected(target_metric)
    {
        result = {};
        result['in'] = false;
        for (var option in selected_metric_result)
        {
            // console.log(selected_metric_result[option]);
            for (var table_title in selected_metric_result[option])
            {
                // console.log(table_title);
                for (var metric_index in selected_metric_result[option][table_title]['metric_result']) {
                    // console.log(selected_metric_result[option][table_title]['metric_result'][metric_index]);
                    if (arr_equal(target_metric,selected_metric_result[option][table_title]['metric_result'][metric_index])) {
                        result['option'] = option;
                        result['table_title'] = table_title;
                        result['metric_index'] = metric_index;
                        result['in'] = true;
                    };
                };
            }
        }
        return result;
    }

    function add_metric_2_selected(option,table_title,table_head,td_content)
    {
        if (! find_metric_in_selected(td_content,selected_metric_result)['in']) {
            if ( ! key_in_dict(option,selected_metric_result)) {
                // console.log("no option");
                selected_metric_result[option] = {};
            }
            if (! key_in_dict(table_title,selected_metric_result[option])) {
                // console.log("no table_title");
                selected_metric_result[option][table_title] = {};
                selected_metric_result[option][table_title]['metric_count'] = 0;
                selected_metric_result[option][table_title]['metric_result'] = [];
                selected_metric_result[option][table_title]['table_head'] = table_head;
            };
            selected_metric_result[option][table_title]['metric_count'] += 1;
            selected_metric_result[option][table_title]['metric_result'].push(td_content);
        };

        // console.log(selected_metric_result);
        
    }

    function rm_metric_2_selected(option,table_title,table_head,td_content)
    {
        find_result = find_metric_in_selected(td_content,selected_metric_result);
        // console.log(find_result);
        if (find_result['in']) {
            selected_metric_result[find_result['option']][find_result['table_title']]['metric_result'].splice(find_result['metric_index'],1);
            selected_metric_result[find_result['option']][find_result['table_title']]['metric_count'] -= 1;
        };
        // console.log(selected_metric_result);
    }

    // search 
    function perform_search(option,search_value)
    {
        // search_value = $(search_input_selector).val();

        $.getJSON('/chart/searchitem/',{option:option,search_value:search_value},function(data)
        {
            after_search(data);
        });
    }

    function after_search(search_result)
    {

        if (search_result.search_result_bool) {
            option = search_result.request_option;
            // clear_search_result_panel();
            render_search_result_to_table(option,search_result.search_result);

        }
        else
        {
            console.log(search_result.info);
        }
    }

    function perform_browse()
    {
        $.getJSON('/chart/browseitem/',function(data)
        {
            after_browse(data);
        })
    }

    function after_browse(browse_result)
    {
        if (browse_result.browse_result_bool) {
            // clear_search_result_panel();
            render_to_browsemetrics_panel(browse_result.browse_result);
        }
        else
        {
            console.log(search_result.info);
        }
    }

    //render basicmetrics_panel

    function clear_search_result_panel()
    {
        $(search_result_panel_selector).empty();
        // $(search_result_panel_selector).resizable();
        // $("#resizable").resizable();
    }

    function render_search_result_to_table(option,metrics)
    {
        // console.log(metrics);
        var result_str = '';
        for (var table_title in metrics) {
            if (metrics[table_title]['metric_count'] > 0) {
                result_str += '<div class="panel panel-default">';
                // result_str += '<div class=' + search_result_div_class + '>';
                result_str += '<div class="panel-heading ' + search_result_table_title_class + '">' + '<b>' + option + '</b>' + option_title_spliter + '<b><I>' + table_title + '</I></b></div>';
                result_str += '<table class="table table-striped ' + search_result_table_class + '">';
                result_str += '<thead><th></th>';
                for (var name in metrics[table_title]['table_head'])
                {
                    result_str += '<th>' + metrics[table_title]['table_head'][name] + '</th>';
                }
                result_str += '</thead>';
                result_str += '<tbody>';
                for (var row in metrics[table_title]['metric_result']) {
                    result_str += '<tr>';
                    // console.log(row);
                    // console.log("before " + table_title,metrics[table_title]['metric_result']);
                    find_result = find_metric_in_selected(metrics[table_title]['metric_result'][row].concat());
                    // console.log("after " + table_title,metrics[table_title]['metric_result']);
                    // console.log(find_result);
                    if (find_result['in']) {
                        result_str += '<td><input type=checkbox class=' + select_metric_input_class + ' checked="checked" /></td>';
                    }
                    else
                    {
                        result_str += '<td><input type=checkbox class=' + select_metric_input_class + ' /></td>';
                    }

                    
                    for (var td in metrics[table_title]['metric_result'][row]) {
                        result_str += '<td>' + metrics[table_title]['metric_result'][row][td] + '</td>';
                    };
                    result_str += '</tr>';
                };
                result_str += '</tbody>';
                result_str += '</table>';
                result_str += '</div>';
            };
        };
        // console.log(result_str);
        $(search_result_panel_selector).append(result_str);
    }

    function render_to_browsemetrics_panel(option_metrics)
    {
        result_str = '';
        // result_str += '<div class="container">';
        result_str += '<div class="container">';
        result_str += '<p class="lead">Cloud Server Metrics by Category</p>';
        result_str += '</div>';

        result_str += '<div class="row">'
        // result_str += '<ul >';
        for (var option in option_metrics) {
            result_str += '<div class="col-sm-2 ">';
            result_str += '<h2><a href="javascript:;" class=' + basic_metrics_first_class + '>' + option + '</a></h2>';
            result_str += '<ul>';
            for (var i = 0; i < option_metrics[option].length; i++) {
                result_str += '<li><a href="javascript:;" class=' + basic_metrics_second_class + '>' + option_metrics[option][i] + '</a></li>';
            }
            result_str += '</ul>';
            result_str += '</div>';

        }
        // result_str += '</ul>';
        result_str += '</div>';
        
        $(basicmetrics_panel_selector).append(result_str);
    }



    // render main
    function render_main_by_page(page)
    {
        switch(page)
        {
            case "dashboard":
                dashboard_render_main();
                break;
            case "billing":
                billing_render_main();
                break;
            case "metric":
                metric_render_main(default_selected,'',true);
                break;
            default:
                break;
        }
    }

	function dashboard_render_main()
	{
        clear_main();
        // hidden_chart();

        if ($(dashboard_main_selector).length <= 0) {
            result_str = '';
            result_str += '<div class="jumbotron ' + dashboard_main_class + '">';
            result_str += '<h1>Metric Summary</h1>';
            result_str += '<p>Monitor monitors operational and performance metrics for your cloud resources and applications.</p>';
            result_str += '<p>Browse or search your metrics to get started graphing data.</p>';

            result_str += '<div class="navbar-form">';
            result_str += browsemetric_button_str;
            result_str += search_input_str;
            result_str +='</div></div>';
                        
            $(main_board_selector).append(result_str);
        }
        else
        {
            $(dashboard_main_selector).removeClass('hidden');
        }
        
	}

	function billing_render_main(option)
	{
        clear_main();
        // show_chart();
        // $(main_board_selector).append();
        // $("div.main").append(option);
	}

	function metric_render_main(option,searched_value,browse_flag)
	{
        // console.log(option);
        clear_main();

        // option = option || default_selected;
        browse_flag = browse_flag || default_browse_flag;
        if (option != undefined) {
            
            add_top_category(option,searched_value);
            if (! browse_flag) {
                add_chart_main_panel();
                add_search_result_panel();
                perform_search(option,searched_value);
                show_chart();
                // console.log("show select");
            }
            else
            {
                hidden_chart();
                add_basicmetric_panel();
                perform_browse();
                // console.log("hidden");
            }
        }
	}

    function get_bind_option()
    {
        result = [];
        $('a[page=metric]').parent().find("li a").each(function(i,d)
        {
            result.push($(this));
        });
        return result;
    }


    function add_top_category(selected_value,searched_value)
    {
        selected_value = selected_value || default_selected;
        searched_value = searched_value || default_searched_value;


        if ($(top_category_main_selector).length <= 0) {
            panel_wrapper = '<div class="panel panel-default ' + top_category_main_class + '" >';
            form_wrapper = '<div class="navbar-form top-category" >';

            

            select_str = '<select class="form-control" id="metricoptions">';
            select_str += '<option>All</option>';
            bind_result = get_bind_option();
            // console.log(bind_result);
            for (var i = 0; i < bind_result.length; i++) {
                if (bind_result[i].attr("option") != undefined) {
                    select_str += '<option>';
                    select_str += bind_result[i].attr("option") + '</option>';
                }
            }

            select_str += '<option>Browse Metrics</option>';

            select_str += '</select>';

            form_wrapper += select_str;
            form_wrapper += '<div class="form-group" >' + search_input_str + '</div>';

            form_wrapper += '</div>';
            // form_wrapper += div_wapper + '</form>';
            panel_wrapper += form_wrapper + '</div>';

            $(main_board_selector).append(panel_wrapper);
        }
        else
        {
            $(top_category_main_selector).removeClass('hidden');
        }

        

        $(search_input_selector).attr("value",searched_value);
        $(option_select_selector).val(selected_value);
    }

    function add_search_result_panel()
    {
        if ($(search_result_panel_selector).length <= 0) {
            var result_str = '';
            result_str += '<div style="height:280px;" class=' + search_result_main_class + '>';
            result_str += '<div class=' + search_result_panel_class + ' ></div>';
            // result_str += '<div id="resizable" class="' + search_result_panel_class + '" style="width: 100px;  height: 100px;  background: #ccc;"></div>';
            result_str += '</div>';

            $(main_board_selector).append(result_str);
            $(search_result_panel_selector).addClass("DivToScroll");
            $(search_result_panel_selector).addClass("DivWithScroll");
            // $('div.search-result-panel').addClass("DivToScroll");
            // $('div.search-result-panel').addClass("DivWithScroll");
            // $(search_result_panel_selector).addClass("ui-widget-content");
            // $(search_result_panel_selector).removeClass(search_result_panel_class);
            // console.log("resizable");
            // $(search_result_panel_selector).resizable();
            // $( search_result_panel_selector ).on( "resize", function( event, ui ) {
            //     console.log("resize");
            // } );

            // var tmp_str = '<div id="resizable" class="nihao" style="width: 100px;  height: 100px;  background: #ccc;"></div>';
            // $(main_board_selector).append(tmp_str);
            $(search_result_main_selector).resizable({
                handles: 's'
            });
        }
        else
        {
            $(search_result_panel_selector).empty();
            $(search_result_main_selector).removeClass('hidden');
        }
        
    }

    // $('#resizable').resizable();

    function add_basicmetric_panel()
    {
        if ($(basicmetrics_panel_selector).length <= 0) {
            $(main_board_selector).append('<div class=' + basicmetrics_panel_class + '></div>');
        }
        else
        {
            $(basicmetrics_panel_selector).empty();
            $(basicmetrics_panel_selector).removeClass('hidden');
            // $(main_board_selector).append('<div class=' + basicmetrics_panel_class + '></div>');
        }
    }

    function add_chart_main_panel()
    {
        if ($(chart_div_selector).length <= 0) {
            result_str = '';
            result_str += '<div class="row ' + chart_div_class + '">';
            result_str += '<div class="col-sm-9 ' + chart_main_div_class + '">';
            result_str += '<div class="row ' + chart_main_header_div_class + '"></div>';
            result_str += '<div class="row ' + chart_main_pagination_class + '"></div>';   
            result_str += '<div class="row ' + chart_main_display_container_class + '"></div>';
            result_str += '</div>';
            result_str += '<div class="col-sm-3 ' + chart_sidebar_config_class + '"></div>';
            result_str += '</div>';

            $(main_board_selector).after(result_str);
            add_panel_to_chart_main_header();
            add_pagination_panel();
            add_chart_sidebar_config_panel();
        }
        else
        {
            $(chart_div_selector).removeClass('hidden');
        }
    }

    function add_pagination_panel()
    {
        result_str = '';
        result_str += '<nav>';
        result_str += '<ul class="pager">';
        result_str += '<li class="previous"><a href="javascript:;" class="' + chart_left_icon_class + '" ><span aria-hidden="true">&larr;</span> Older</a></li>';
        result_str += '<li class="next"><a href="javascript:;" class="' + chart_right_icon_class + '">Newer <span aria-hidden="true">&rarr;</span></a></li>';
        result_str += '</ul>';
        result_str += '</nav>';
        $(chart_main_pagination_selector).append(result_str);
    }

    function add_chart_sidebar_config_panel()
    {
        use_utc = chart_config['use_utc'];

        var result_str = '';
        result_str += '<div class="form-horizontal">';

        timezone = -((new Date()).getTimezoneOffset()/60);
        signed_tag = '';
        if (timezone > 0) {
            signed_tag = '+';
        }
        else
        {
            signed_tag = '-';
        }

        result_str += '<div class="form-group">';
        result_str += '<div class="col-md-10 col-md-offset-1">';
        result_str += '<label class="radio-inline"><input type="radio" name=' + utc_radio_class + ' class=' + utc_radio_class + ' value=1>UTC (GMT)</label>';
        result_str += '<label class="radio-inline"><input type="radio" name=' + utc_radio_class + ' class=' + utc_radio_class + ' value=0 checked>Local (GMT ' + signed_tag + timezone + ':00)</label>';
        result_str += '</div>';
        result_str += '</div>';

        result_str += '<div class="form-group">';
        result_str += '<label class="col-md-2 control-label">From</label>';
        result_str += '<div class="col-md-8">';
        result_str += '<div class="input-group date ' + from_time_class + '">';
        result_str += '<input type="text" class="form-control" />';
        result_str += '<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>';
        result_str += '</div>';
        result_str += '</div>';
        result_str += '</div>';

        result_str += '<div class="form-group">';
        result_str += '<label class="col-md-2 control-label">To</label>';
        result_str += '<div class="col-md-8">';
        result_str += '<div class="input-group date ' + to_time_class + '">';
        result_str += '<input type="text" class="form-control" />';
        result_str += '<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>';
        result_str += '</div>';
        result_str += '</div>';
        result_str += '</div>';

        

        result_str += '<div class="form-group">';
        result_str += '<div class="col-md-8 col-md-offset-2">';
        result_str += '<a type="submit" class="btn btn-primary ' + update_graph_button_class + '">update graph</a>';
        result_str += '</div>';
        result_str += '</div>';


        result_str += '<div class="form-group">';
        result_str += '<label class="col-md-2 control-label">Zoom</label>';
        result_str += '<div class="col-md-8">';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="3600">1h</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="10800">3h</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="21600">6h</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="43200">12h</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="86400">1d</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="259200">3d</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="604800">1w</a></label>';
        result_str += '<span>|</span>';
        result_str += '<label class="control-label"><a class="control-label ' + zoom_type + '" href="javascript:;" value="1209600">2w</a></label>';
        result_str += '</div>';
        result_str += '</div>';

        result_str += '</div>';

        result_str += '<div class=' + sidebar_config_message_class + '></div>';

        $(chart_sidebar_config_selector).append(result_str);

        $(from_time_selector).datetimepicker({
            pick12HourFormat: false
        });
        $(to_time_selector).datetimepicker({
            pick12HourFormat: false,
        });
        // $(to_time_selector).data("DateTimePicker").


        $(from_time_selector).on("dp.change",function (e) {
            $(to_time_selector).data("DateTimePicker").setMinDate(e.date);
            var from_clock = time_convert_second(chart_config['use_utc'],e.date);
            chart_config['from_clock'] = from_clock;
            // console.log($(to_time_selector).data("DateTimePicker"));
        });
        $(to_time_selector).on("dp.change",function (e) {
            $(from_time_selector).data("DateTimePicker").setMaxDate(e.date);
            var to_clock = time_convert_second(chart_config['use_utc'],e.date);
            chart_config['to_clock'] = to_clock;
        });
        
        // clear_sidebar_config_message();
        // add_message_2_sidebar_config_message('from time is lessthan to time','danger');
        // $(sidebar_config_message_selector).append('<div class="alert alert-danger"> </div>');
    }



    function clear_sidebar_config_message()
    {
        $(sidebar_config_message_selector).empty();
    }

    function add_message_2_sidebar_config_message(message,type)
    {
        result_str = '';
        result_str += '<div class="alert alert-' + type + '">';
        result_str += '<button type="button" class="close" data-dismiss="alert">&times;</button>';
        result_str += message;
        result_str += '</div>';
        
        $(sidebar_config_message_selector).append(result_str);
        setTimeout(function()
        {
            $(sidebar_config_message_selector).empty();
        },5000);
        // $(sidebar_config_message_selector).append('<div class="alert alert-' + type + '">' + message + '');
    }


    function add_panel_to_chart_main_header()
    {
        function_type = chart_config['function_type'];
        frequency = chart_config['frequency'];


        result_str = '';
        result_str += '<div class="panel panel-default" style="margin-bottom:0px;">';
        result_str += '<div class="panel-heading">';
        result_str += '<div class="form-inline">';

        result_str += '<select class="form-control ' + function_type_class + '">';
        result_str += '<option>Average</option>';
        result_str += '<option>Minimum</option>';
        result_str += '<option>Maximum</option>';
        result_str += '<option>Sum</option>';
        result_str += '<option>Count</option>';
        result_str += '</select>';

        result_str += '<select class="form-control ' + frequency_setting_class + '" style="margin-left:10px">';
        result_str += '<option value=60>1 Minutes</option>';
        result_str += '<option value=10>10 Seconds</option>';
        result_str += '<option value=14400>4 Hours</option>';
        result_str += '</select>';

        result_str += '<a class="btn btn-default form-control ' + refresh_icon_class + '"><span class="glyphicon glyphicon-refresh"></span></a>';

        result_str += '</div>';
        result_str += '</div>';
        result_str += '</div>';
        $(chart_main_header_div_selector).append(result_str);
        $(function_type_selector).val(function_type);
        $(frequency_setting_selector).val(frequency);
    }


    function clear_main()
    {
        // $(main_board_selector).empty();
        // display_chart.clear_chart();
        // hidden_chart();

        $(dashboard_main_selector).addClass('hidden');
        $(top_category_main_selector).addClass('hidden');
        $(search_result_main_selector).addClass('hidden');
        $(basicmetrics_panel_selector).addClass('hidden');
        $(chart_div_selector).addClass('hidden');
    }

    function all_clear()
    {
        display_chart.clear_chart();
    }

    function hidden_chart()
    {
        $(chart_div_selector).addClass('hidden');
    }

    function show_chart()
    {
        $(chart_div_selector).removeClass('hidden');
    }

    function make_active(class_selector,target)
    {
        $(class_selector).removeClass("active");
        target.addClass("active");
    }

    this.get_selected_metric_result = function()
    {
        return selected_metric_result;
    }

    this.get_chart_config = function()
    {
        return chart_config;
    }

    this.set_smr_cc = function(local_selected_metric_result,local_chart_config)
    {
        var tmp_smr = jQuery.extend(true, {}, local_selected_metric_result);
        var tmp_cc = jQuery.extend(true, {}, local_chart_config);
        selected_metric_result = tmp_smr;
        chart_config = tmp_cc;

        chart_config['container_class'] = chart_main_display_container_class;
        chart_config['container_selector'] = chart_main_display_container_selector;
    }

    this.get_display_chart = function()
    {
        return display_chart;
    }

    this.update_call = function()
    {
        chart_update();
    }

}
