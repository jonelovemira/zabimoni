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
    oit = gen_operational_itemtype()
    monthes = odmonth.get_all_timestr()
    return render_template('odata/main.html', title='Operational Data', \
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
