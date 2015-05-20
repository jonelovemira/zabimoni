function load_indexes()
{
    $('div[type=displayname][indextype=service]').each(function(i,d)
    {
        indexId = $(this).attr("value");
        // d.popover({});
        $('div[type=displayname][indextype=service][value=' + indexId + ']').popover({
            html:true,
            trigger:'manual',
            content: function()
            {
                console.log('test');
                return $('div[serviceid=' + $(this).attr("value") + ']').html();
            }
        });
    });
    
    $('div[class=IndexDiv]').hide();

    $('div[class=IndexDiv][type=service]').show();
}



function find_all_checked(check_result)
{
        // console.log("find_all_check");
        var current_area_id_list = [];
        var current_service_id_list = [];
        var current_host_id_list = [];
        var current_aws_id_list = [];
        var current_area_name_list = [];
        var current_service_name_list = [];
        var current_host_name_list = [];
        var current_aws_name_list = [];
        //find all area checked
        $("input[indextype=area]").each(function(i,d){
            // console.log("D.VALUE",d.value);
            if (d.checked){
                // console.log("D.VALUE",d.value);
                current_area_id_list.push(d.value);
                current_area_name_list.push(d.name);
            }
        });

        //find all service checked
        $("input[indextype=service]").each(function(i,d){
            if (d.checked){
                current_service_id_list.push(d.value);
                current_service_name_list.push(d.name);
            }
        });

        //find all host checked
        $('div[info=servicepopover]').find('input[indextype=host][locate=popover]').each(function(i,d)
        {
            // console.log($(this).attr("checked"));
            if ($(this).attr("checked") == 'checked') {
                current_host_name_list.push(d.name);
                current_host_id_list.push(d.value);
            }
        });

        // $("input[indextype=host]").each(function(i,d){
        //     if (d.checked) {
        //         current_host_name_list.push(d.name);
        //         current_host_id_list.push(d.value);
        //     }
        // });

        //find all aws checked
        $("input[indextype=aws]").each(function(i,d){
            if (d.checked){
                current_aws_name_list.push(d.name);
                current_aws_id_list.push(d.value);
            }
            
        });
        // console.log(current_host_id_list);
        check_result['area'] = '';
        check_result['service'] = '';
        check_result['host'] = '';
        check_result['aws'] = '';
        check_result['names'] = {};
        if (current_area_id_list.length > 0) {
            check_result['area'] = current_area_id_list.join('@');
            check_result['names']['area'] = current_area_name_list.join(';');
        }

        if (current_service_id_list.length > 0) {
            check_result['names']['service'] = current_service_name_list.join(';');
            check_result['service'] = current_service_id_list.join('@');
        };
        if (current_host_id_list.length > 0)
        {
            check_result['names']['host'] = current_host_name_list.join(';');
            check_result['host'] = current_host_id_list.join('@');
        }
        if (current_aws_id_list.length > 0) {
            check_result['names']['aws'] = current_aws_name_list.join(';');
            check_result['aws'] = current_aws_id_list.join('@');
        };        
}

function clear_panel()
{
    $('div[class=panel-body]').empty();
}

function refresh_item_container(check_result)
{
    // $('div[class=itemContainer]').empty();
    clear_panel();
    find_all_checked(check_result);
	// find_all_checked(check_result);
    console.log(check_result);
	var area = check_result['area'];
    var service = check_result['service'];
    var host = check_result['host'];
    var aws = check_result['aws'];

    $.getJSON('/chart/itemtype',{area:area,service:service,host:host,aws:aws},function(data)
    {
        clear_panel();
        console.log(data);
        if (data.itemtype != undefined) {
            for (data_it in data.itemtype) {
                // console.log(data.itemtype[data_it]);
                // console.log(data[data_it].items);
                value = data.itemtype[data_it].items.join('@');
                name = data.itemtype[data_it].name;
                itemdatatype = data.itemtype[data_it].itemdatatypename;
                time_frequency = data.itemtype[data_it].time_frequency;
                // console.log(itemdatatypename);
                // $('div[class=itemContainer]').append('<div typename='+);
                html_tag = '<button class="btn btn-sm btn-default itemtype" value=' + value + ' itemtypeid=' + data_it + ' name="' + name + '" time_frequency=' + time_frequency + '>' + name + '</button>' ;
                $('div[itemdatatype="' + itemdatatype + '"]').append(html_tag);
            };
            // $('input[type=checkbox][locate=index][indextype=host]')[0].parentNode.hide();
            // console.log($('input[type=checkbox][locate=index][indextype=host]'));
            // $('div[class=col-sm-3][indextype=host]').hide();
            // for (var i = data.hostids.length - 1; i >= 0; i--) {
            //     $('div[class=col-sm-3][indextype=host][value=' + data.hostids[i] + ']').show();
            // }
        };
        
        // $('div[input=checkbox][locate=index][indextype=host][value=' +  + ']')
    })
}



function save_window_chart(wc_name,series)
{
    var option = {  
        url: '/chart/save/window',
        type: 'POST',
        data: JSON.stringify({'wc_name':wc_name,'series':series}),
        dataType: 'json',
        contentType : 'application/json', 
        success: function (data) {
            id = data.id;
            if(id != undefined)
            {
                id = data.id;
                name = data.name;
                $('div[udf=savedlist]').append('<button class="btn btn-sm btn-default savedListItemButton" indexId=' + id + ' name="' + name + '">' + name 
                    +  '<span class="glyphicon glyphicon-remove" aria-hidden="true" style="margin-left:10px" indexId=' + id + '></span></button>');
            }
            $('#forsaving').modal('hide');
        }  
    };  
    $.ajax(option);
}

function save_page_chart(pagename,series_info)
{
    var option = {  
        url: '/chart/save/page',
        type: 'POST',
        data: JSON.stringify({'pagename':pagename,'series_info':series_info}),
        dataType: 'json',
        contentType : 'application/json', 
        success: function (data) {
            id = data.id;
            if (id != undefined) {
                id = data.id;
                name = data.name;
                $('div[udf=savedlist]').append('<button class="btn btn-sm btn-default savedListItemButton" indexId=' + id + ' name="' + name + '">' + name 
                    +  '<span class="glyphicon glyphicon-remove" aria-hidden="true" style="margin-left:10px" indexId=' + id + '></span></button>');
            };
            $('#forsaving').modal('hide');
        }  
    };  
    $.ajax(option);
}


function find_and_gen(classname)
{
    // $('a[class=indexbutton][name=' + classname + ']').empty();
    //     $('div[class=checkedIndex][type=' + classname + ']').empty();
    tmp = [];
    count = 0;
        $("input[indextype=" + classname + "]").each(function(i,d){
            if (d.checked) {
                  // $('div[class=checkedIndex][type=' + classname + ']').append('<button class=checkbutton type='+classname + ' value=' + d.value + '>' + classname + ':' + d.name + '</button>')  ;            
                count += 1;
                tmp.push(d.name);    
            }
        });
        $('span[class=badge][indextype=' + classname + ']').empty();
        if (count > 0) {
            str = tmp.join('\n');
            $('a[class=indexbutton][name=' + classname + ']').attr("title",str);
            $('span[class=badge][indextype=' + classname + ']').append(count);
        }
        else
        {
            $('a[class=indexbutton][name=' + classname + ']').attr("title",'');
        }
        
        // console.log(tmp);
}


function generate_display_name(name,check_result)
{
        // console.log("check_result",check_result);
        find_all_checked(check_result);
        tmp = '';
        dic = {0:'area',1:'service',2:'host',3:'aws'};
        for (var i in check_result['names']) {
            tmp += i + ':' + check_result['names'][i] + '**';
        };
        tmp += name;
        return tmp;
}


$(document).on('click','a.indexbutton',function()
{
        $('div[class=IndexDiv]').hide();
        name = $(this).attr("name");
        $('div[type=' + name +']').show();
        $('li[choose=monitorWindowLi]').attr("class","");
        $('li[type=' + name + ']').attr("class","active");
});



$(document).on('click','button[class=checkbutton]',function()
{
    type = $(this).attr("type");
    value = $(this).attr("value");
    shaixuan = 'input[type=checkbox][class=' + type + '][value=' + value
             + ']';
    $('input[type=checkbox][class=' + type + '][value=' + value + ']').attr("checked",false);
    $(this).remove();
    
});

$(document).on('change','input[type=checkbox][locate=index]',function()
{
    classname = $(this).attr("indextype");
    value = $(this).attr("value");
    checked_value = $(this)[0].checked;
    if (classname == 'service') {
        $('input[locate=popover][indextype=host][serviceid=' + value + ']').attr("checked",checked_value);
        $('input[locate=popover][indextype=host][serviceid=' + value + ']').prop("checked",checked_value);
        
    };
        // console.log('change');
        find_and_gen(classname);
        check_result = {};
        refresh_item_container(check_result);
});



$(document).on('click','div[type=displayname]',function(e)
{
    // $(this).popover({
    //     html:true,
    //     content:function()
    //     {
    //         return $('div[serviceid=' + $(this).attr("value") + ']').html();
    //     }
    // })
    // $(this).popover('hide');

    $(this).popover('toggle');
    return false;
});

$(document).on('click','input[type=checkbox][locate=popover][indextype=host]',function()
{
    hostid = $(this).attr("value");
    serviceid = $(this).attr("serviceid");
    var orig = $('div[info=servicepopover][serviceid=' + serviceid + ']').find('input[locate=popover][value=' + hostid + ']');
    checked_value = $(this)[0].checked;
    orig.attr("checked",checked_value);
    // orig.prop("checked",checked_value);
    
    
    var all_host_checked_value = false;
    {
        
        $('input[indextype=host][locate=popover][serviceid=' + serviceid + ']').each(function(i,d)
        {
            // console.log(d);
            // console.log($(this).prop("checked"));
            // console.log($(this).prop("checked"));
            // console.log($(this)[0].checked);
            if ($(this).prop("checked")) {
                // console.log(d);
                all_host_checked_value = true;
            };
        })
    }

    // console.log(all_host_checked_value);

    $('input[indextype=service][locate=index][value=' + serviceid + ']').attr("checked",all_host_checked_value);
    $('input[indextype=service][locate=index][value=' + serviceid + ']').prop("checked",all_host_checked_value);

    var check_result = {};
    find_and_gen('service');
    check_result = {};
    refresh_item_container(check_result);
    console.log(check_result);
});





// $(document).on('click','input[type=checkbox][locate=tooltip]',function()
// {
//     hostid = $(this).attr("hostid");
//     // $(this).attr("checked","true");
//     checked_value = $(this)[0].checked;
//     // console.log('bind');
//     console.log("checked_value",checked_value);
//     // console.log($(this));
//     // if (checked_value) {
//     //     $('input[type=checkbox][indextype=host][value=' + hostid + ']').attr("checked",checked_value);
//     // }
//     // else
//     // {
//     //     console.log("remove");
//     //     $('input[type=checkbox][indextype=host][value=' + hostid + ']').removeAttr("checked");
//     // }
//     $('input[type=checkbox][indextype=host][value=' + hostid + ']').prop('checked',checked_value);
//     // change_value = $('input[type=checkbox][indextype=host][value=' + hostid + ']').attr("checked");
//     // console.log("after_change",change_value);
// });



