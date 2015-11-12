import json
from flask import Blueprint, request, render_template, flash, g, \
        redirect, url_for

from flask.ext.principal import RoleNeed, UserNeed, Permission
from flask.ext.login import login_required

admin_permission = Permission(RoleNeed('1')).union(Permission(RoleNeed('0')))

mod_odata = Blueprint('odata', __name__, url_prefix='/odata', template_folder \
    = 'templates')

from monitor.odata.models import *
from monitor.functions import gen_operational_itemtype, str_2_clock


@mod_odata.route('/')
@login_required
def odata_main():
    
    return render_template('odata/main.html', title='Operational Data')

@mod_odata.route('/mechine')
@login_required
def mechine_main():
    oit = gen_operational_itemtype()
    monthes = odmonth.get_all_timestr()
    return render_template('odata/mechine_main.html', title='Operational Data', \
        oit=oit, monthes=monthes)

@mod_odata.route('/monthdata', methods=['POST', 'GET'])
@login_required
def monthdata():
    result = {}
    load_result_bool = False
    load_result = {}
    info = None
    try:
        month = request.args.get('month',None)
        # time = 'March 2015'
        if month is None:
            raise Exception('Invalid args, month cannot be None')

        clock = str_2_clock(month, '%B %Y')

        odm = odmonth.query.filter_by(beginclock=clock).first()
        load_result['data'] = []
        if odm is not None:
            load_result['data'] = odm.gen_table_content()

        load_result['month'] = month
        info = 'success'
        load_result_bool = True

    except Exception, e:
        info = str(e)
        print info
        load_result = {}
        load_result_bool = False

    result['load_result'] = load_result
    result['load_result_bool'] = load_result_bool
    result['info'] = info

    return json.dumps(result)


@mod_odata.route('/userdevice')
@login_required
def userdevice_main():
    region_data = {}
    for r in region.query.all():
        region_data[r.regionshort] = r.regionlong

    month_data = count.get_all_month_str()


    return render_template('odata/userdevice_main.html', \
        title='Operational Data', region_data=region_data, month_data=month_data)

@mod_odata.route('/r_m_uddata', methods=['POST', 'GET'])
@login_required
def region_month_userdevice_data():
    result = {}
    load_result_bool = False
    load_result = {}
    info = None
    try:
        month = request.form.get("month", None)
        regionshort = request.form.get("region", None)
        # time = 'March 2015'
        if month is None or regionshort is None:
            raise Exception('Invalid args, month or region cannot be None')

        clock = str_2_clock(month, '%B %Y')
        r = region.query.filter_by(regionshort=regionshort).first()
        if r is None:
            raise Exception(' region input does not exist')
        

        rc_result = {}
        region_counts = r.counts.filter('clock >=' + str(clock)).all()
        for rc in region_counts:
            if rc.clock not in rc_result:
                rc_result[rc.clock] = {}

            rc_result[rc.clock][rc.counttype.counttypename] = rc.value
        


        load_result['data'] = rc_result
        info = 'success'
        load_result_bool = True

    except Exception, e:
        info = str(e)
        print info
        load_result = {}
        load_result_bool = False

    result['load_result'] = load_result
    result['load_result_bool'] = load_result_bool
    result['info'] = info

    return json.dumps(result)
            