import json, sys, traceback
from flask import Blueprint, request, render_template, flash, g, session, \
        redirect, url_for

from flask.ext.principal import RoleNeed, UserNeed, Permission
from flask.ext.login import login_required

mod_billing = Blueprint('billing', __name__, url_prefix='/billing')

admin_permission = Permission(RoleNeed('1')).union(Permission(RoleNeed('0')))

from monitor.billing.models import *
from monitor.functions import str_2_clock, opentime_from_month_csv

@mod_billing.route('/')
@login_required
@admin_permission.require(http_exception=403)
def billing_main():
    time_str_arr = billingtime.get_all_timestr()
    return render_template('billing/billsreport.html', title='billing', \
        time_arr=time_str_arr)


@mod_billing.route('/billsreport', methods=['POST', 'GET'])
@login_required
@admin_permission.require(http_exception=403)
def billsreport():
    result = {}
    info = None
    load_result_bool = False
    load_result = {}
    try:
        time = request.args.get('time',None)
        # time = 'March 2015'
        if time is None:
            raise Exception('Invalid args, time cannot be None')

        clock = str_2_clock(time, '%B %Y')
        consolidated_bill_data = {}
        for s in awsservice.query.all():
            tmps_r = s.build_list(clock)
            if len(tmps_r['region_info']) > 0:
                consolidated_bill_data[s.productname] = tmps_r


        linkedaccount_data = {}
        for l in linkedaccount.query.all():
            if l.fee_of_time(clock) is None:
                continue
            linkedaccount_data[l.linkedaccountname] = l.fee_of_time(clock)

        summary_data = {}
        summary_data['Total'] = 0
        summary_data['payers'] = {}
        for p in payeraccount.query.all():
            if p.fee_of_time(clock) is None:
                continue
            summary_data['Total'] += p.fee_of_time(clock)
            summary_data['payers'][p.payeraccountid] = {}
            summary_data['payers'][p.payeraccountid]['Total'] = \
                p.fee_of_time(clock)
            summary_data['payers'][p.payeraccountid]['InvoiceDate'] = \
                p.billingrows.filter_by(billingperiodstartdate=clock)\
                    .first().invoicedate

        region_data = {}
        region_data['Total'] = 0
        region_data['regions'] = {}
        for az in availablezone.query.all():
            tmp_fee = az.fee_of_time(clock)
            if tmp_fee is None:
                continue
            region_data['Total'] += tmp_fee
            region_data['regions'][az.regionname] = {}
            region_data['regions'][az.regionname]['Total'] = tmp_fee
            region_data['regions'][az.regionname]['lc'] = {}
            for l in linkedaccount.query.all():
                if az.fee_of_time(clock, l) is not None:
                    region_data['regions'][az.regionname]['lc']\
                    [l.linkedaccountname] = az.fee_of_time(clock, l)

        load_result['time'] = time
        load_result['consolidated_bill_data'] = consolidated_bill_data
        load_result['linkedaccount_data'] = linkedaccount_data
        load_result['summary_data'] = summary_data
        load_result['region_data'] = region_data
        info = 'success'
        load_result_bool = True
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        info = str(e)

    result['info'] = info
    result['load_result_bool'] = load_result_bool
    result['load_result'] = load_result

    return json.dumps(result)


@mod_billing.route('/billsreport/la', methods=['POST', 'GET'])
@login_required
@admin_permission.require(http_exception=403)
def ladata():
    result = {}
    info = None
    load_result_bool = False
    load_result = {}
    try:
        time = request.args.get('time', None)
        linkedaccountname = request.args.get('laname', None)
        load_collapse_id = request.args.get('render_selector_id', None)
        # time = 'March 2015'
        if time is None or linkedaccountname is None:
            raise Exception('Invalid args')

        l = linkedaccount.query.filter_by(linkedaccountname=linkedaccountname).first()
        if l is None:
            raise Exception('Linked account do not exist with name:' + linkedaccountname)

        clock = str_2_clock(time, '%B %Y')

        load_result['data'] = l.build_list(clock)

        load_result['time'] = time
        load_result['laname'] = linkedaccountname
        load_result['load_collapse_id'] = load_collapse_id
        info = 'success'
        load_result_bool = True

    except Exception, e:
        info = str(e)
        load_result_bool = False
        load_result = None

    result['info'] = info
    result['load_result_bool'] = load_result_bool
    result['load_result'] = load_result

    return json.dumps(result)
