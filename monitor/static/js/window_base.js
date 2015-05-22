function window_base(content_height,content_width)
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
    var dashboard_main_height = $(dashboard_main_selector).height();

    //billing top category
    billing_top_category_class = 'billing-top-category';
    billing_top_category_selector = 'div.' + billing_top_category_class;
    billing_search_input_str = '<input type=text class="form-control billing-search" placeholder="input Metrics Name"/>';
    billing_search_input_selector = 'input.billing-search';



    main_board_selector = "div.indexmain";
    selected_metric_li_class = 'selected-metrics';
    selected_metric_li_selector = 'li.' + selected_metric_li_class;

    // top category config
    top_category_main_class = 'top-category-main';
    top_category_main_selector = 'div.' + top_category_main_class;
    top_category_selector = "div.top-category";
    browsemetric_button_str = "<button class='btn btn-primary form-control browsemetric' type='button'>Browse Metrics</button>"
    browsemetric_button_selector = "button.browsemetric";
    dashboard_search_input_str = '<input type=text class="form-control dashboard-search" placeholder="input Metrics Name" width="330px" />';
    main_search_input_str = '<input type=text class="form-control main-search" placeholder="input Metrics Name" width="330px" />';
    db_search_input_selector = "input.dashboard-search";
    main_search_input_selector = "input.main-search";
    search_input_class = "search";
    default_selected = 'Browse Metrics';
    default_searched_value = '';
    option_select_selector = '#metricoptions';

    //search result panel
    search_result_main_class = "search-result-main"; 
    search_result_main_selector = 'div.' + search_result_main_class; 
    search_result_panel_class = "search-result-panel";
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
    chart_main_div_selector = 'div.' + chart_main_div_class;
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

    shared_yaxis_class = 'shared-yaxis';
    shared_yaxis_selector = 'select.' + shared_yaxis_class;


    // sidebar save , load

    sidebar_save_class = 'save';
    sidebar_save_selector = 'button.' + sidebar_save_class;
    sidebar_load_class = 'sidebar-load';
    sidebar_load_selector = 'a.' + sidebar_load_class;
    sidebar_load_ul_selector = 'ul.sidebar-load-ul';
    sidebar_load_li_class = 'chart-saved-li';
    sidebar_load_li_selector = 'a.' + sidebar_load_li_class;

    sidebar_load_remove = 'remove';
    sidebar_load_remove_selector = 'span.' + sidebar_load_remove;

    sidebar_savename_class = 'save-name';
    sidebar_savename_selector = 'input.' + sidebar_savename_class;


    uncheck_all_class = 'uncheck-all';
    uncheck_all_selector = 'a.' + uncheck_all_class;
    check_all_class = 'check-all';
    check_all_selector = 'a.' + check_all_class;
    max_checked_count = 10;

    filter_class = 'table-head-filter';
    filter_selector = 'a.' + filter_class;
    clear_filter_class = 'clear-filter';
    clear_filter_selector = 'span.' + clear_filter_class;

    var filter_span = '<span class="glyphicon glyphicon-remove ' + clear_filter_class + '" aria-hidden="true"></span>' ;

    var meaningful_td_content_length = 4;

    // flag for if browse or search
    default_browse_flag = false;

    table_title_used_index = {
        'per_instance_result' : [2,3],
        'by_group_result' : [0,1]
    }

    // default_update_search_table = true;


    // global variables
    var selected_metric_result = {};

    //chart configurations
    var chart_config = {};
    var display_chart = new chart();

    set_default_chart_config();
    add_select();



    // add_top_category('All','');
    // $(top_category_main_selector).addClass("hidden");
    // console.log($(top_category_main_selector));

    allow_check_multiple_flag = true;

    function set_default_chart_config()
    {
        chart_config['frequency'] = 60;
        chart_config['function_type'] = 'Average';
        chart_config['container_class'] = chart_main_display_container_class;
        chart_config['container_selector'] = chart_main_display_container_selector;
        chart_config['use_utc'] = false;
        chart_config['init_time_length'] = 60 * 60;
        chart_config['update_flag'] = true;
        chart_config['shared_yaxis'] = true;
    }



    // calc_init_chart_height();
    set_init_height();
    // add_chart_main_panel();
    var other_height;
    this.div_main_height = null;
    var whole_height = content_height;
    // console.log(this.div_main_height);

    this.div_chart_height = null;
    this.top_category_height = null;

    var chart_main_display_height;
    var chart_main_display_width;
    var current_object = this;
    // var chart_main_header_config_height;
    // var chart_main_pagination_height;
    // $(window).load(function () {
        
    // });

    this.window_load_set = function()
    {
        this.div_chart_height = $(chart_div_selector).height();
        this.top_category_height = $(top_category_main_selector).height();
        // console.log(div_chart_height,top_category_height);
        var chart_main_header_config_height = $(chart_main_header_div_selector).height();
        var chart_main_pagination_height = $(chart_main_pagination_selector).height();
        // console.log(chart_main_header_config_height,chart_main_pagination_height);
        // console.log(top_category_height);
        chart_main_display_height = this.div_chart_height - chart_main_header_config_height - chart_main_pagination_height + 40;
        chart_main_display_width = $(chart_main_display_container_selector).width();
        $(chart_main_display_container_selector).height(chart_main_display_height);
        $(chart_div_selector).addClass("hidden");
        $(top_category_main_selector).addClass("hidden");
        other_height = this.div_chart_height + this.top_category_height;
    }
    
    function set_init_height()
    {
        $('div.main').height(whole_height);
    }



    this.resize_caller = function(tmp_height,tmp_width)
    {
        current_object.div_main_height = tmp_height;
        $('div.main').height(current_object.div_main_height);
        var chart_hidden_flag = false;
        var top_category_hidden_flag = false;

        if ($(chart_div_selector).attr("class") != undefined) {

            chart_hidden_flag = $(chart_div_selector).attr("class").indexOf("hidden") > 0;
        };

        if ($(top_category_main_selector).attr("class") != undefined) {

            top_category_hidden_flag = $(top_category_main_selector).attr("class").indexOf("hidden") > 0;
        };


        $(chart_div_selector).removeClass("hidden");
        $(top_category_main_selector).removeClass("hidden");

        chart_main_display_width = $(chart_main_header_div_selector).width();
        var chart_main_header_config_height = $(chart_main_header_div_selector).height();
        var chart_main_pagination_height = $(chart_main_pagination_selector).height();
        chart_main_display_height = $(chart_sidebar_config_selector).outerHeight() - chart_main_header_config_height - chart_main_pagination_height - 10 + 4;
        current_object.div_chart_height = $(chart_sidebar_config_selector).outerHeight() + 4;
        $(chart_main_display_container_selector).height(chart_main_display_height);
        $(chart_main_display_container_selector).width(chart_main_display_width);

        if (display_chart.get_chart() != undefined) {
            display_chart.get_chart().setSize(chart_main_display_width,chart_main_display_height,false);
        };

        var tmp_top_category_height = $(top_category_main_selector).height();



        other_height = current_object.div_chart_height + tmp_top_category_height;
        $(search_result_main_selector).height(current_object.div_main_height - 10 - other_height - 5);
        $(search_result_main_selector).resizable("option","maxHeight",current_object.div_main_height - 10 - 5 - 50 - 99 );

        if (chart_hidden_flag) {
            $(chart_div_selector).addClass("hidden");
        };

        if (top_category_hidden_flag) {
            $(top_category_main_selector).addClass("hidden");
        };
    }

    function arr_equal(compareFrom,compareTo,tmp_table_title) {
        if (!compareTo || compareFrom.length != compareTo.length) {
            return false;
        }
        if (table_title_used_index[tmp_table_title] != undefined) {
            for (var i = 0; i < table_title_used_index[tmp_table_title].length; i++) {
                if (compareFrom[table_title_used_index[tmp_table_title][i]] != compareTo[table_title_used_index[tmp_table_title][i]]) {
                    return false;
                }
            }
            return true;
        }
        else
        {
            for (var i = 0; i < compareFrom.length; ++i) {
                if (i == 4) {
                    continue;
                };
                if (compareFrom[i] != compareTo[i]) {
                    return false;
                }
            }
            return true;
        }
        
    };


	$(sidebar_page_li_selector).click(function()
	{
        target = $(this);
		make_active(sidebar_page_li_selector,target);
	});

    $(document).on('keypress',db_search_input_selector,function(event)
    {
        if ( event.which == 13) {
            option = 'All';
            search_value = $(this).val();
            option = option || default_selected;
            search_value = search_value || default_searched_value;
            metric_render_main(option,search_value);
        };
    });

    // $(main_search_input_selector).on("keyup click",function()
    // {
    //     console.log($(this).val());
    // })

    $(document).on('keyup click',main_search_input_selector,function(event)
    {
        search_value = $(this).val();
        // console.log($(this).val());
        if ( event.which == 13) {
            option = $(option_select_selector).val();
            // search_value = $(this).val();
            option = option || default_selected;
            search_value = search_value || default_searched_value;
            metric_render_main(option,search_value);
        }
        else
        {
            if (current_table_id_arr != undefined) {
                for (var i = 0; i < current_table_id_arr.length; i++) {
                    $("#" + current_table_id_arr[i]).DataTable().search(
                        search_value,false,true).draw();
                };
            };
            
        }

        
    });

    $(document).on('keyup click',billing_search_input_selector,function(event)
    {
        search_value = $(this).val();
        // if ( event.which == 13) {
        //     search_value = $(this).val();
        //     // metric_render_main(search_value);
        //     billing_render_main(search_value)
        // };
        // console.log(search_value);
        for (var i = 0; i < current_table_id_arr.length; i++) {
            $("#" + current_table_id_arr[i]).DataTable().search(
                search_value,false,true).draw();
        };
    });

    $(document).on('change',option_select_selector,function()
    {
        option = $(this).val();
        // metric_render_main(option);
        if (option == 'Browse Metrics') {
            metric_render_main(option,'',true);
        }
        else
        {
            // console.log("change in callback");
            metric_render_main(option);
        }
    });

    $(document).on('click',sidebar_page_selector,function()
    {
        clear_main();
        page = $(this).attr("page");
        option = $(this).attr("option");
        // hidden_chart();
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
        // hidden_chart();
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
        $(this).closest('div.panel').find('.' + search_result_table_title_class).each(function(i,d)
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
            if ($(this).text().length > 0 ) {
                td_content.push($(this).text());
            }
            else
            {
                if (td_content.length > 0) {
                    td_content.push('');
                };
            }
        });

        // console.log(table_head,td_content);

             

        metrics_checkbox_result = $(this).prop("checked");
        // console.log(td_content);

        select_metric_change(option,table_title,table_head,td_content,metrics_checkbox_result);
        chart_update();
    });
    

    $(document).on('click',selected_metric_li_selector,function(event)
    {
        render_current_selected_metrics();
    });

    function render_current_selected_metrics()
    {
        // console.log('in render current sm',$(chart_main_div_selector));

        clear_main();
        add_top_category('All','');
        // add_search_result_message();

        var pre_set_filter_str = '';
        // pre_set_filter_str += '<ul class="nav nav-pills" role="tablist" style="border-bottom:solid 1px #bbb;padding-bottom:2px;">';
        // pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">per_instance_result<span class="glyphicon glyphicon-remove ' + clear_filter_class + '" aria-hidden="true"></span></a></li>';
        // pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">by_group_result<span class="glyphicon glyphicon-remove ' + clear_filter_class + '" aria-hidden="true"></span></a></li>';
        // pre_set_filter_str += '</ul>';
        add_chart_main_panel();
        add_search_result_panel();

        // console.log("data in render_current_selected_metrics",selected_metric_result);
        // show_chart();
        for (var option in selected_metric_result)
        {
            var tmp_metric_count = 0;
            for (var table_title in selected_metric_result[option]) {
                tmp_metric_count += selected_metric_result[option][table_title]['metric_count'];
            }
            if (tmp_metric_count > 0) {
                render_search_result_to_table(option,selected_metric_result[option]);
            };
            
        }
        $(message_selector).empty();
    }


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

    $(document).on('change',shared_yaxis_selector,function()
    {
        var tmp_shared_yaxis = $(this).val();
        if (tmp_shared_yaxis == '0') {
            chart_config['shared_yaxis'] = false;
        }
        else
        {
            chart_config['shared_yaxis'] = true;
        }
        chart_update();
    });


    $(document).on('click',zoom_type_selector,function()
    {
        var init_time_length = $(this).attr("value");
        chart_config['init_time_length'] = parseInt(init_time_length);
        // console.log(chart_config['to_clock']);
        // if (chart_config['to_clock'] == undefined) {
        var now = (new Date()).getTime();
        chart_config['update_flag'] = false;
        chart_config['to_clock'] = now / 1000;
        chart_config['from_clock'] = chart_config['to_clock'] - init_time_length;
        set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
        set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
        // }
        // else
        // {
        //     if (chart_config['to_clock'] > init_time_length) {
        //         chart_config['from_clock'] = chart_config['to_clock'] - init_time_length;
        //         set_date_to_timepicker(from_time_selector,chart_config['from_clock']);
        //         set_date_to_timepicker(to_time_selector,chart_config['to_clock']);
        //     };
        // }
        
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
        set_default_chart_config();

        var function_type = $(function_type_selector).val();
        var frequency = $(frequency_setting_selector).val();

        var tmp_shared_yaxis = $(shared_yaxis_selector).val();
        if (tmp_shared_yaxis == '0') {
            chart_config['shared_yaxis'] = false;
        }
        else
        {
            chart_config['shared_yaxis'] = true;
        }
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
        if (time_range != null && time_range != undefined && time_range.dataMin != null && time_range.dataMax != null) {
            var from_in_ms = parseInt(time_range.dataMin);
            var to_in_ms = parseInt(time_range.dataMax);
            var new_from = to_in_ms;
            var new_to = to_in_ms + (to_in_ms - from_in_ms);

            chart_config['from_clock'] = new_from / 1000 + 60;
            chart_config['to_clock'] = new_to / 1000 + 120;
            // console.log("chart exist right");

            
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
        // console.log(time_range);
        if (time_range != null && time_range != undefined && time_range.dataMin != null && time_range.dataMax != null) {
            var from_in_ms = parseInt(time_range.dataMin);
            var to_in_ms = parseInt(time_range.dataMax);
            var new_from = from_in_ms - (to_in_ms - from_in_ms);
            var new_to = from_in_ms ;

            chart_config['from_clock'] = new_from / 1000 ;
            chart_config['to_clock'] = new_to / 1000 ;
            chart_update();
            // console.log("chart exist left");
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


    $(document).on('click',sidebar_save_selector,function()
    {
        // console.log('save');
        // var windowname = 'test';
        var windowname = $(sidebar_savename_selector).val();
        // console.log(windowname);
        if (windowname != undefined && windowname != null && windowname != '') {
            // console.log(chart_config);
            save_chart( selected_metric_result,chart_config, windowname);
        }
        else
        {
            alert('Saved name cannot be empty');
        }

        
    });

    $(document).on('click',sidebar_load_li_selector,function()
    {
        var indexId = $(this).attr("indexId"); 
        // var windowid = 11;
        // console.log($(chart_main_div_selector));
        load_chart(indexId);
    });

    $(document).on('click',sidebar_load_remove_selector,function(event)
    {
        var indexId = $(this).attr("indexId");
        var windowname = $(this).closest('a').attr("name");
        // console.log(windowname);
        if (confirm('Are you sure to delete window: ' + windowname)) {
            delete_chart(indexId);
            // console.log("windowname:",windowname);
        }
        event.stopPropagation();
    });

    $(document).on('click',check_all_selector,function()
    {
        // console.log("check all");
        $(search_result_panel_selector).find(select_metric_input_selector).each(function(i,d)
        {
            var metric_count = get_selected_metric_count();
            if (metric_count < max_checked_count) {
                $(this).prop("checked","checked");

                var title_text = null;
                $(this).closest('div.panel').find('.' + search_result_table_title_class).each(function(i,d)
                {
                    title_text = $(this).text();
                });

                var option_title = title_text.split(option_title_spliter);
                var option = option_title[0];
                var table_title = option_title[1];

                // console.log(option,table_title);


                var table_head = [];
                $(this).closest('table').find('th').each(function(i,d)
                {
                    // console.log($(this).text().length);
                    if ($(this).text().length > 0) {
                        table_head.push($(this).text());
                    };
                });

                var td_content = [];
                $(this).closest('tr').find('td').each(function(i,d)
                {
                    if ($(this).text().length > 0) {
                        td_content.push($(this).text());
                    }
                    else
                    {
                        if (td_content.length > 0) {
                            td_content.push('');
                        };
                    }
                });


                select_metric_change(option,table_title,table_head,td_content,true);
            }
            else
            {
                add_message_2_query_message_selector('You can choose at most : ' + max_checked_count + ' metrics' , 'danger')
            }
            
        });
        
        // console.log(selected_metric_result);
        chart_update();
    });

    $(document).on('click',uncheck_all_selector,function()
    {
        var change_flag = false;
        // console.log($(search_result_panel_selector).find(select_metric_input_selector));
        $(search_result_panel_selector).find(select_metric_input_selector).each(function(i,d)
        {
            if (d.checked) {
                change_flag = true;
                $(this).removeAttr("checked");


                var title_text = null;
                $(this).closest('div.panel').find('.' + search_result_table_title_class).each(function(i,d)
                {
                    title_text = $(this).text();
                });

                var option_title = title_text.split(option_title_spliter);
                var option = option_title[0];
                var table_title = option_title[1];

                // console.log(option,table_title);


                var table_head = [];
                $(this).closest('table').find('th').each(function(i,d)
                {
                    // console.log($(this).text().length);
                    if ($(this).text().length > 0) {
                        table_head.push($(this).text());
                    };
                });

                var td_content = [];
                $(this).closest('tr').find('td').each(function(i,d)
                {
                    if ($(this).text().length > 0) {
                        td_content.push($(this).text());
                    }
                    else
                    {
                        if (td_content.length > 0) {
                            td_content.push('');
                        };
                    }
                });

                // console.log(table_title,td_content)
                select_metric_change(option,table_title,table_head,td_content,false);
            };
        });
        
        if (change_flag) {
            // console.log("update");
            chart_update();
        };
        
        // select_metric_change();
    });

    function delete_chart(indexId)
    {
        $.getJSON('/chart/delete/window',{windowid:indexId},function(data)
        {
            if (data.delete_result_bool) {
                var windowid = data.delete_result;
                // console.log($(sidebar_load_ul_selector).find('a[indexId="' + windowid +'"]'));
                $(sidebar_load_ul_selector).find('a[indexId="' + windowid +'"]').each(function(i,d)
                {
                    $(this).closest('li').remove();
                });
            }
            else
            {
                add_message_2_query_message_selector(data.info,'danger');
            }
        });
    }



    function save_chart(saved_selected_metrics,saved_chart_config,saved_windowname)
    {
        var option = {  
            url: '/chart/save/window',  
            type: 'POST',  
            data: JSON.stringify({'selected_metrics':saved_selected_metrics,'chart_config':saved_chart_config,'windowname':saved_windowname}),  
            dataType: 'json', 
            contentType : 'application/json', 
            success: function (data) {
                // console.log(data);
                if (data.save_result_bool) {
                    result_str = '<li>';
                    result_str += '<a href="javascript:;" class="' + sidebar_load_li_class 
                            + '" indexId="' + data.save_result['indexId'] + '" name="' + data.save_result['name'] + '">' + data.save_result['name'] ;
                    result_str += '<span class="glyphicon glyphicon-remove remove" aria-hidden="true" indexId="' + data.save_result['indexId'] + '"></span>'
                    result_str += '</a>';
                    result_str += '</li>';
                    $(sidebar_load_ul_selector).append(result_str);
                }
                else
                {
                    // console.log(data.info);
                    add_message_2_query_message_selector(data.info,'danger');
                }
                $(sidebar_savename_selector).val('');
            }  
        };  
        $.ajax(option);
    }

    this.update_select_badge_from_outer = function()
    {
        update_select_badge();
    }

    this.render_current_selected_metrics_from_outer = function()
    {
        render_current_selected_metrics();
    }

    function load_chart(saved_windowid)
    {
        $.getJSON('/chart/load/window',{windowid:saved_windowid},function(data)
        {
            if (data.load_result_bool) {
                // console.log('after load',$(chart_main_div_selector));

                selected_metric_result = {};
                selected_metric_result = data.load_result['selected_metrics'];

                // console.log("data in load_chart",selected_metric_result);
                chart_config = {};
                // console.log("before",chart_config)
                chart_config = data.load_result['chart_config'];
                // console.log("after",chart_config['use_utc']);
                update_select_badge();
                render_current_selected_metrics();
                chart_update();
            }
            else
            {
                add_message_2_query_message_selector(data.info,'danger');
            }
        });
    }


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

            if ( !allow_check_multiple_flag ) {
                selected_metric_result = {};

                $(search_result_panel_selector).find(select_metric_input_selector).each(function(i,d)
                {
                    if (d.checked) {

                        var tmp_td_content = [];
                        $(this).closest('tr').find('td').each(function(i,d)
                        {
                            if ($(this).text().length > 0) {
                                tmp_td_content.push($(this).text());
                            };
                        });

                        if (!arr_equal(tmp_td_content,td_content,table_title)) {
                            $(this).removeAttr("checked");
                        };

                    };
                });
            };   

            add_metric_2_selected(option,table_title,table_head,td_content);
        }
        else
        {
            rm_metric_2_selected(option,table_title,table_head,td_content);
        }
        
        // console.log(selected_metric_result);

        update_select_badge();


        // set_default_chart_config();
        

    }

    function get_selected_metric_count()
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
        return metric_count;
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
        if (chart_config['update_flag'] == undefined || chart_config['update_flag'] == null) {
            chart_config['update_flag'] = true;
        };
        if (chart_config['update_flag']) {
            // chart_config['init_time_length'] = 3600;
            if (chart_config['init_time_length'] == undefined || chart_config['init_time_length'] == true) {
                chart_config['init_time_length'] = 3600;
            };
        }
        else
        {

            if (chart_config['to_clock'] == undefined || chart_config['to_clock'] == null ) {
                var now = (new Date()).getTime() / 1000 ;
                chart_config['to_clock'] = now  ;
            }
            
            if (chart_config['from_clock'] == undefined || chart_config['from_clock'] == null) {
                chart_config['from_clock'] = chart_config['to_clock']  - 3600;
            };
            // console.log(chart_config);
        }

        if (chart_config['frequency'] == undefined || chart_config['frequency'] == null) {
            chart_config['frequency'] = 60;
        }

        if (chart_config['function_type'] == undefined || chart_config['function_type'] == null) {
            chart_config['function_type'] = 'Average';
        }

        $('input.' + utc_radio_class + '[value=' + chart_config['use_utc'] +']').prop("checked", true);
        

        if (chart_config['use_utc'] == "0") {
            chart_config['use_utc'] = false;
        }
        else if(chart_config['use_utc'] == "1")
        {
            chart_config['use_utc'] = true;
        }

        if (chart_config['shared_yaxis'] == "0") {
            chart_config['shared_yaxis'] = false;
        }
        else if(chart_config['shared_yaxis'] == "1")
        {
            chart_config['shared_yaxis'] = true;
        }


    }

    function update_chart_main_header(tmp_chart_config)
    {
        var tmp_function_type = tmp_chart_config['function_type'];
        var tmp_update_frequency = tmp_chart_config['frequency'];
        var tmp_shared_yaxis = tmp_chart_config['shared_yaxis'];

        // console.log(tmp_shared_yaxis);
        if (tmp_shared_yaxis == false) {
            tmp_shared_yaxis = "0";
        }
        else if (tmp_shared_yaxis == true)
        {
            tmp_shared_yaxis = "1";
        }
        else
        {
            tmp_shared_yaxis = "1";
        }
        $(function_type_selector).val(tmp_function_type);
        $(frequency_setting_selector).val(tmp_update_frequency);
        $(shared_yaxis_selector).val(tmp_shared_yaxis);
    }

    function chart_update()
    {
        check_chart_config(chart_config);
        check_result = check_selected_metric();
        if (check_result) {
            update_chart_main_header(chart_config);
            display_chart.set_selected_metrics(selected_metric_result);
            display_chart.set_chart_config(chart_config);
            display_chart.clear_chart();
            display_chart.set_highchart();
            display_chart.create_chart();
        }
        else
        {
            display_chart.clear_chart();
        }
        // else
        // {
        //     add_message_2_query_message_selector('No selected metric currently','danger');
        // }

        // setTimeout(function()
        // {
        //     if (display_chart.get_chart() == null) {
        //         $(chart_config['container_selector']).empty();
        //         add_message_2_query_message_selector('load chart time out','danger');
        //     };
        // },5000)
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
                    if (arr_equal(target_metric,selected_metric_result[option][table_title]['metric_result'][metric_index], table_title)) {
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
        var metric_count = get_selected_metric_count();
        if (metric_count < max_checked_count) {
            if (! find_metric_in_selected(td_content)['in'] ) {
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
        }
        else
        {
            add_message_2_query_message_selector('You can choose at most : ' + max_checked_count + ' metrics' , 'danger');
        }
        

        // console.log(selected_metric_result);
        
    }

    function rm_metric_2_selected(option,table_title,table_head,td_content)
    {
        find_result = find_metric_in_selected(td_content);
        // console.log(find_result);
        if (find_result['in']) {
            selected_metric_result[find_result['option']][find_result['table_title']]['metric_result'].splice(find_result['metric_index'],1);
            selected_metric_result[find_result['option']][find_result['table_title']]['metric_count'] -= 1;
        };
        // console.log(selected_metric_result);
    }

    var last_search;

    // search 
    function perform_search(route,args)
    {
        // search_value = $(search_input_selector).val();

        //route = '/chart/searchitem/';
        if (last_search ) {
            last_search.abort();
        };

        var find_cache_result = before_search_check(args);
        if (find_cache_result == null) {
            search_result_panel_waiting();
            last_search = $.getJSON(route,args,function(data)
            {
                search_result_panel_waiting_cancel();
                // console.log(current_class);
                if (data.search_result_bool) {
                    current_class.search_result_cache[data.args.option] = data;
                };
                after_search(data,data.args);
            });
        }
        else
        {
            after_search(find_cache_result,args);
        }
    }

    function after_search(search_result,args)
    {
        if (search_result.search_result_bool) {
            // option = search_result.request_option;
            option = args.option;
            // clear_search_result_panel();

            $(search_result_panel_selector).find('.panel').each(function(i,d)
            {
                $(this).remove();
            });

            var tmp_table_head = args.table_head;
            var tmp_search_result;
            if (tmp_table_head != undefined && tmp_table_head != null) {
                var new_tmp_search_result = jQuery.extend(true, {}, search_result.search_result);
                for (var tmp_key in new_tmp_search_result) {
                    if (tmp_key != tmp_table_head) {
                        delete new_tmp_search_result[tmp_key];
                    }
                }
                tmp_search_result = new_tmp_search_result;
            }
            else
            {
                tmp_search_result = search_result.search_result;
            }
            // console.log(search_result.search_result);
            // render_search_result_to_table(option,search_result.search_result);
            render_search_result_to_table(option,tmp_search_result);

            $(main_search_input_selector).click();
            // add_message_2_query_message_selector(search_result.info,'success');
        }   
        else
        {
            // console.log(search_result.info);
            add_message_2_query_message_selector(search_result.info,'danger');
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

    $(document).on('click',filter_selector,function()
    {
        make_active('li[role=presentation]',$(this).closest('li'));
        $(filter_selector + ' > span').remove();
        $(this).append(filter_span);
        var table_head = $(this).text();
        var option = '';
        $('.top-category').each(function(i,d)
        {
            // console.log($(this).parent());
            // console.log($(this).parent().hasClass('hidden'));
            if(!$(this).parent().hasClass('hidden'))
            {
                // console.log($(this));
                $(this).find('select').each(function(i,d)
                {
                    option = $(this).val();
                })
            }
        })
        // var search_value = $(main_search_input_selector).val();
        var search_value = '';
        args = {option:option,search_value:search_value,table_head:table_head};
        perform_search('/chart/searchitem/',args);
    });

    this.search_result_cache = {};

    var current_class = this;


    function before_search_check(args)
    {
        var tmp_search_option = args.option;
        if (current_class.search_result_cache != undefined) {
            if (current_class.search_result_cache[tmp_search_option] != undefined) {
                return current_class.search_result_cache[tmp_search_option];
            };
        };
        return null;
    }

    $(document).on('click',clear_filter_selector,function(event)
    {
        // console.log("clear_filter_selector");
        $('li[role=presentation]').removeClass('active');
        var option = '';
        $('.top-category').each(function(i,d)
        {
            // console.log($(this).parent());
            // console.log($(this).parent().hasClass('hidden'));
            if(!$(this).parent().hasClass('hidden'))
            {
                // console.log($(this));
                $(this).find('select').each(function(i,d)
                {
                    option = $(this).val();
                })
            }
        })
        var search_value = $(main_search_input_selector).val();
        args = {option:option,search_value:search_value};
        perform_search('/chart/searchitem/',args);
        this.remove();
        event.stopPropagation();
    });

    var current_table_id_arr;

    function render_search_result_to_table(option,metrics)
    {
        // $(search_result_panel_selector).find('.panel').each(function(i,d)
        //     {
        //         $(this).remove();
        //     });
        // console.log(metrics);
        var result_str = '';
        var display_metric_result_count = 0;

        
        for (var table_title in metrics) {
            display_metric_result_count += metrics[table_title]['metric_count'];
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
                        if (td == 4) {
                            if (metrics[table_title]['metric_result'][row][td] == 2) {
                                result_str += '<td>' + '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" style="color:#a94442"></span><div class="hidden">' + metrics[table_title]['metric_result'][row][td] + '</div>' + '</td>';
                            }
                            else if(metrics[table_title]['metric_result'][row][td] == 1)
                            {
                                result_str += '<td>' + '<span class="glyphicon glyphicon-ok-sign" aria-hidden="true" style="color:#3c763d"></span><div class="hidden">' + metrics[table_title]['metric_result'][row][td] + '</div>' + '</td>';
                            }
                            else
                            {
                                result_str += '<td>' + '<span class="glyphicon glyphicon-question-sign" aria-hidden="true" ></span><div class="hidden">' + 3 + '</div>' + '</td>';
                            }
                        }
                        else{
                            result_str += '<td>' + metrics[table_title]['metric_result'][row][td] + '</td>';
                        }
                    };
                    result_str += '</tr>';
                };
                result_str += '</tbody>';
                result_str += '</table>';
                result_str += '</div>';
            };
        }
        if (result_str == '') {
            show_specific_child(search_result_panel_selector,message_class);
            add_message_2_query_message_selector('Have No Metrics Result. Please try a different.','info');
        }
        else
        {
            show_all_child(search_result_panel_selector);
            // add_message_2_query_message_selector('Showing the <b>' + display_metric_result_count + '</b> matching metrics. You can refine your search or try Browsing Metrics.','info');
        

        }
        // console.log(result_str);
        if (result_str != '') {
            // console.log("data in render_search_result_to_table",metrics);
            $(search_result_panel_selector).append(result_str);

            current_table_id_arr = [];
            $(search_result_panel_selector).find('.' + search_result_table_class).each(function(i,d)
            {

                if ($(this).attr("id") == undefined) {
                    // console.log($(this));
                    $(this).dataTable({
                        // "searching":false,
                        "paging":false,
                        // "bFilter": false,
                    });
                };
                current_table_id_arr.push($(this).attr("id")); 
            });
        };
    }

    var waiting_class_span = 'waiting-span';
    var waiting_class_selector = 'span.' + waiting_class_span;

    function search_result_panel_waiting () {
        
        var result_str = '';

        result_str += '<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate ' + waiting_class_span + '"></span>';

        if ($(search_result_panel_selector).length > 0){
            $(search_result_panel_selector).append(result_str);
        }  
    }

    function search_result_panel_waiting_cancel () {
        // body...
        if ($(search_result_panel_selector).length > 0){
            $(search_result_panel_selector + '>' + waiting_class_selector).remove();
        } 
    }

    function show_specific_child(parent,visiable_child)
    {
        // console.log($(parent).children());
        $(parent).children().each(function(i,d)
        {
            $(this).removeClass("hidden");
            var current_class_name = $(this).attr("class");
            // console.log(visiable_child,current_class_name);
            if (current_class_name != visiable_child) {
                $(this).addClass("hidden");
            }
            else{
                $(this).removeClass("hidden");
            }
        });
    }

    function show_all_child(parent)
    {
        $(parent).children().each(function(i,d)
        {
            $(this).removeClass("hidden");
        });
    }

    function render_to_browsemetrics_panel(option_metrics)
    {

        var result_str = '';
        // result_str += '<div class="form-group">';
        result_str += '<p class="lead">Cloud Server Metrics by Category</p>';
        // result_str += '</div>';

        
        for (var option in option_metrics) {
            result_str += '<div class="form-inline" style="border-bottom:1px solid #bbb;">'
            result_str += '<h2><a href="javascript:;" class="' + basic_metrics_first_class + '" >' + option + '</a></h2>';
            for (var i = 0; i < option_metrics[option].length; i++) {
                result_str += '<a type="button" style="margin-right:10px;margin-bottom:10px;" href="javascript:;" class="btn btn-default form-control ' + basic_metrics_second_class + '">' + option_metrics[option][i] + '</a>';
            }
            result_str += '</div>';
        }


        
        // result_str += '</div>';

        
        $(basicmetrics_panel_selector).append(result_str);
        // $(basicmetrics_panel_selector).addClass("")
        // $(basicmetrics_panel_selector).addClass("DivToScroll");
        // $(basicmetrics_panel_selector).addClass("DivWithScroll");
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
                billing_render_main('');
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
            result_str += dashboard_search_input_str;
            result_str +='</div></div>';
                        
            $(main_board_selector).append(result_str);
        }
        else
        {
            $(dashboard_main_selector).removeClass('hidden');
        }
        
	}

	function billing_render_main(searched_value)
	{
        clear_main();
        // show_chart();
        // $(main_board_selector).append();
        // $("div.main").append(option);
        // add_search_result_message();
        add_billing_top_category();

        var pre_set_filter_str = '';
        pre_set_filter_str += '<ul class="nav nav-pills hidden" role="tablist" style="border-bottom:solid 1px #bbb;padding-bottom:2px;">';
        pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By All</a></li>';
        pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By ServiceName and LinkedAccount</a></li>';
        pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By ServiceName</a></li>';
        pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By LinkedAccount</a></li>';
        pre_set_filter_str += '</ul>';

        add_chart_main_panel();
        add_search_result_panel(pre_set_filter_str);

        // searched_value = searched_value || 'EC2';

        if (searched_value == undefined || searched_value == null) {
            searched_value = 'EC2';
        };
        var args = {option:'billing',search_value:searched_value}
        perform_search('/chart/searchitem/',args);
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
                // add_search_result_message();
                var pre_set_filter_str = '';
                if (option == 'billing') {
                    pre_set_filter_str += '<ul class="nav nav-pills hidden" role="tablist" style="border-bottom:solid 1px #bbb;padding-bottom:2px;">';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By All</a></li>';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By ServiceName and LinkedAccount</a></li>';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By ServiceName</a></li>';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">By LinkedAccount</a></li>';
                    pre_set_filter_str += '</ul>';
                }
                else
                {
                    pre_set_filter_str += '<ul class="nav nav-pills hidden" role="tablist" style="border-bottom:solid 1px #bbb;padding-bottom:2px;">';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">per_instance_result</a></li>';
                    pre_set_filter_str += '<li role="presentation"><a href="javascript:;" class="' + filter_class + '">by_group_result</a></li>';
                    pre_set_filter_str += '</ul>';
                }
                
                
                add_chart_main_panel();
                add_search_result_panel(pre_set_filter_str);
                
                args = {option:option,search_value:searched_value}
                perform_search('/chart/searchitem/',args);
                // show_chart();
                // console.log("show select");
            }
            else
            {
                // hidden_chart();
                add_basicmetric_panel();
                perform_browse();
                // console.log("hidden");
            }
        }

        // console.log($(top_category_main_selector).attr("class"));        
        // console.log($())
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

    function add_billing_top_category(searched_value)
    {
        // console.log("add_billing_top_category");

        if ($(billing_top_category_selector).length <= 0) {
            result_str = '';
            result_str += '<div class="panel panel-default ' + billing_top_category_class + '" >';
            result_str += '<div class="navbar-form top-category" >';
            result_str += '<select class="form-control">';
            result_str += '<option checked>billing</option>';
            result_str += '</select>';
            result_str += '<div class="form-group" >' + billing_search_input_str + '</div>';
            result_str += '</div>';
            result_str += '</div>';

            if ($(message_selector).length > 0) {
                $(message_selector).before(result_str);
            }
            else
            {
                $(main_board_selector).append(result_str);
            }
        }
        else
        {
            $(billing_top_category_selector).removeClass('hidden');
        }

        $(billing_search_input_selector).attr("value",searched_value);
    }

    function add_select()
    {
        $.getJSON('/item/service_json',function(data)
        {
            if (data.load_service_result_bool) {

                result_str = '';
                result_str = '<select class="form-control" id="metricoptions">';
                result_str += '<option>All</option>';
                result_str += '<option>Basic Metrics</option>';
                bind_result = data.load_service_result;
                // console.log(bind_result);
                for (var i = 0; i < bind_result.length; i++) {
                    if (bind_result[i] != undefined) {
                        result_str += '<option>';
                        result_str += bind_result[i] + '</option>';
                    }
                }
                result_str += '<option>billing</option>';
                result_str += '<option>Browse Metrics</option>';

                result_str += '</select>';

                $(main_search_input_selector).closest('div').before(result_str);

                // $('div.top-category').append(result_str);

                // form_wrapper += '<div class="form-group" >' + '<input type=text class="form-control main-search" placeholder="input Metrics Name" value="' + searched_value + '" autocomplete="on" />' + '</div>';


                
            }
            else
            {
                add_message_2_query_message_selector(data.info,'danger');
            }
                
        })
    }


    function add_top_category(selected_value,searched_value)
    {
        selected_value = selected_value || default_selected;
        searched_value = searched_value || default_searched_value;


        if ($(top_category_main_selector).length <= 0) {

            $.getJSON('/item/service_json',function(data)
            {
                if (data.load_service_result_bool) {
                    panel_wrapper = '<div class="panel panel-default ' + top_category_main_class + '" >';
                    form_wrapper = '<div class="navbar-form top-category" >';

                    

                    select_str = '<select class="form-control" id="metricoptions">';
                    select_str += '<option>All</option>';
                    select_str += '<option>Basic Metrics</option>';
                    bind_result = data.load_service_result;
                    // console.log(bind_result);
                    for (var i = 0; i < bind_result.length; i++) {
                        if (bind_result[i] != undefined) {
                            select_str += '<option>';
                            select_str += bind_result[i] + '</option>';
                        }
                    }

                    select_str += '<option>Browse Metrics</option>';

                    select_str += '</select>';

                    form_wrapper += select_str;
                    form_wrapper += '<div class="form-group" >' + '<input type=text class="form-control main-search" placeholder="input Metrics Name" value="' + searched_value + '" autocomplete="on" />' + '</div>';

                    form_wrapper += '</div>';
                    // form_wrapper += div_wapper + '</form>';
                    panel_wrapper += form_wrapper + '</div>';

                    if ($(message_selector).length > 0) {
                        $(message_selector).before(panel_wrapper);
                    }
                    else
                    {
                        $(main_board_selector).append(panel_wrapper);
                    }
                }
                else
                {
                    add_message_2_query_message_selector(data.info,'danger');
                }
                
            });
            

            
        }
        else
        {
            $(top_category_main_selector).removeClass('hidden');
        }

        // console.log("search_value",searched_value );
        $(main_search_input_selector).attr("value",searched_value);
        $(main_search_input_selector).prop("value",searched_value);

        $(option_select_selector).val(selected_value);
    }

    // $(chart_div_selector).load(function() {
    //     console.log("chart:",$(this).height());
    // });
    
    this.set_other_height = function(height)
    {
        // this.div_chart_height = height;
        // console.log(this.div_chart_height);
        other_height = height;
        // console.log(height);
    }

    this.set_display_container_width = function(width)
    {
        chart_main_display_width = width;
        // console.log(width);
    }

    function add_search_result_panel(tmp_pre_set_filter_str)
    {
        // console.log(this.div_chart_height);
        if ($(search_result_panel_selector).length <= 0) {

            // this.div_chart_height = $(chart_div_selector).height();
            // this.top_category_height = $(top_category_main_selector).height();
            // console.log(this.div_main_height,this.div_chart_height,this.top_category_height);
            // console.log(tmp_panel_height);
            var tmp_category_height = $(top_category_main_selector).height();
            if (tmp_category_height <= 0) {
                tmp_category_height = $(billing_top_category_selector).height();
            }

            if (tmp_category_height <= 0) {
                tmp_category_height = 50;
            };

            var tmp_other_height = $(chart_div_selector).height() + tmp_category_height ;

            var panel_height = whole_height - 10 - tmp_other_height - 5;
            // console.log($(chart_div_selector).height() , $(top_category_main_selector).height());
            // console.log("panel_height",panel_height);
            // console.log("this.div_main_height",whole_height);
            
            // console.log('add search_result panel',$(chart_main_div_selector));


            var result_str = '';

            


            result_str += '<div style="height:' + panel_height + 'px;" class=' + search_result_main_class + '>';
            // result_str += '<'
            result_str += '<div class=' + search_result_panel_class + ' >';
////
////
/////
//// to do  
            
            result_str += '<div class="' + message_class + ' hidden"></div>';

            if (tmp_pre_set_filter_str != undefined) {
                result_str += tmp_pre_set_filter_str;
            };
            
            result_str += '<div class="tmp hidden" >';
            result_str += '<a href="javascript:;" class="' + check_all_class + '" style="margin-left:15px">Check All </a>';
            result_str += '/';
            result_str += '<a href="javascript:;" class="' + uncheck_all_class + '">Uncheck All </a>';
            // result_str += '<div id="resizable" class="' + search_result_panel_class + '" style="width: 100px;  height: 100px;  background: #ccc;"></div>';
            result_str += '</div>';
            result_str += '</div></div>';

            $(main_board_selector).append(result_str);
            $(search_result_panel_selector).addClass("DivToScroll");
            $(search_result_panel_selector).addClass("DivWithScroll");

            $(search_result_main_selector).resizable({
                handles: 's',
                maxHeight: this.div_main_height - 10 - 5 - 50 - 99 ,
                stop:function(event,ui)
                {
                    var div_change_height = ui.size.height - ui.originalSize.height;
                    var chart_change_height = 0 - div_change_height;
                    var chart_origin_height = $(chart_main_display_container_selector).height();
                    $(chart_main_display_container_selector).height(chart_origin_height + chart_change_height);
                    var tmp_chart_main_display_width = $(chart_main_header_div_selector).width();
                    if (display_chart.get_chart() != undefined) {
                        display_chart.get_chart().setSize(tmp_chart_main_display_width,chart_origin_height + chart_change_height,false);
                    };
                }
            });
        }
        else
        {
            $(search_result_panel_selector).empty();
            var result_str = '';
            result_str += '<div class="' + message_class + ' hidden"></div>';
            if (tmp_pre_set_filter_str != undefined) {
                result_str += tmp_pre_set_filter_str;
            };
            result_str += '<div class="tmp hidden" >';
            result_str += '<a href="javascript:;" class="' + check_all_class + '" style="margin-left:15px">Check All </a>';
            result_str += '|';
            result_str += '<a href="javascript:;" class="' + uncheck_all_class + '">Uncheck All </a>';
            result_str += '</div>';
            $(search_result_panel_selector).append(result_str);
            $(search_result_main_selector).removeClass('hidden');
        }
        
    }

    function add_search_result_message()
    {
        if ($(message_selector).length <= 0) {
            var result_str = '';
            result_str += '<div class="' + message_class + '"></div>';
            $(main_board_selector).append(result_str);
        }
        else
        {
            $(message_selector).empty();
            $(message_selector).removeClass('hidden');
        }
    }

    // $('#resizable').resizable();

    function add_basicmetric_panel()
    {
        if ($(basicmetrics_panel_selector).length <= 0) {
            $(main_board_selector).append('<div class="panel ' + basicmetrics_panel_class + '"></div>');
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
        // console.log('add chart before',$(chart_main_div_selector));

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

        var tmp_div_chart_height = $(chart_div_selector).height();
        var tmp_top_category_height = $(top_category_main_selector).height();

        if (tmp_top_category_height <= 0) {
            tmp_top_category_height = $(billing_top_category_selector).height();
        }

        if (tmp_top_category_height <= 0) {
            tmp_top_category_height = 50;
        };
        // console.log(div_chart_height,top_category_height);
        var tmp_chart_main_header_config_height = $(chart_main_header_div_selector).height();
        var tmp_chart_main_pagination_height = $(chart_main_pagination_selector).height();
        // console.log(chart_main_header_config_height,chart_main_pagination_height);
        // console.log(top_category_height);
        var tmp_chart_main_display_height = tmp_div_chart_height - tmp_chart_main_header_config_height - tmp_chart_main_pagination_height - 10;
        // chart_main_display_width = $(chart_main_display_container_selector).width();
        $(chart_main_display_container_selector).height(tmp_chart_main_display_height);
        // console.log('add chart after',$(chart_main_div_selector));

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
        else if ( timezone < 0)
        {
            signed_tag = '-';
        }
        else
        {
            signed_tag = '';
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
            format: 'YYYY/MM/DD HH:mm',
            // pickSeconds: false,
            pick12HourFormat: false,
            autoclose:true 
        });
        $(to_time_selector).datetimepicker({
            format: 'YYYY/MM/DD HH:mm',
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

    function add_message_2_query_message_selector(message,type)
    {
        result_str = '';
        result_str += '<div class="alert alert-' + type + '">';
        result_str += '<button type="button" class="close" data-dismiss="alert">&times;</button>';
        result_str += message;
        result_str += '</div>';

        // if ($(message_selector).length <= 0) {
        //     add_search_result_message();        
        // };

        // var origin_height = $(message_selector).height();
        // console.log(origin_height);
        $(message_selector).empty();
        $(message_selector).append(result_str);
        // setTimeout(function()
        // {
        //     $(message_selector).empty();
        // },5000);
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
        result_str += '<option value=10>10 Seconds</option>';
        result_str += '<option value=60>1 Minute</option>';
        result_str += '<option value=180>3 Minutes</option>';
        result_str += '<option value=300>5 Minutes</option>';
        result_str += '<option value=900>15 Minutes</option>';
        result_str += '<option value=1800>30 Minutes</option>';
        result_str += '<option value=3600>1 Hours</option>';
        result_str += '<option value=14400>4 Hours</option>';
        result_str += '<option value=86400>1 Day</option>';
        result_str += '</select>';

        result_str += '<select class="form-control ' + shared_yaxis_class + '" style="margin-left:10px">';
        result_str += '<option value=1>Shared yAxis</option>';
        result_str += '<option value=0>Individual yAxis</option>';
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
        $(billing_top_category_selector).addClass('hidden');
        $(message_selector).addClass('hidden');
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
        metric_render_main('All','',false);
        chart_update();
    }

    this.set_allow_check_multiple = function(flag)
    {
        allow_check_multiple_flag = flag;
    }

    this.is_select_empty = function()
    {
        return !check_selected_metric();
    }

    this.set_default_cc_caller = function()
    {
        set_default_chart_config();
    }
}
