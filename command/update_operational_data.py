#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor, config

from config import BY_GROUP_RESULT, MONITOR_TYPE
from monitor import db
from monitor.odata.models import *
from monitor.chart.indextable import *
from monitor.chart.displaychart import Chart
from monitor.functions import gen_operational_itemtype
import time

import boto.dynamodb2
import collections

DAY_INTERVAL = 86400
SUM_INDEX = 5

now = int(time.time())
timeto = now // DAY_INTERVAL * DAY_INTERVAL
timefrom = timeto - DAY_INTERVAL


def update():
    itindex = gen_operational_itemtype()
    beginclock = timefrom - ((time.gmtime(timefrom).tm_mday - 1) * DAY_INTERVAL)

    om = odmonth.query.filter_by(beginclock=beginclock).first()
    if om is None:
        om = odmonth(beginclock)
        db.session.add(om)

    m_index = 0

    for itobj in itindex:
        history = intervaldata.query.filter_by(timefrom=timefrom, \
            timeto=timeto,groupname=itobj["groupname"], \
            itemkey=itobj["itemkey"]).all()
        # print history
        for h in history:
            db.session.delete(h)

        rcgf = RowContentGeneratorFactory()
        by_group_gen = rcgf.produce_generator(BY_GROUP_RESULT)
        fake_row = by_group_gen.get_fake_row(itobj["groupname"], \
            itobj["itemkey"])
        item_list = by_group_gen.content_2_id(fake_row)

        vals = Chart.item_list_2_history_data(item_list, DAY_INTERVAL, \
            timefrom, timeto)

        if len(vals) > 0:
            # print itobj["groupname"], itobj["itemkey"]
            default_v = vals[0][SUM_INDEX]
            if m_index == 0 or m_index == 1:
                default_v = vals[0][SUM_INDEX] * 7.5
            itvd = intervaldata(timefrom, timeto, itobj["groupname"], \
                itobj["itemkey"], itobj["displayname"], default_v, om)
            db.session.add(itvd)

        m_index += 1

    db.session.commit()

def update_counts():
    REGIONS = dict(sg='ap-southeast-1', us='us-east-1', ie='eu-west-1',
                   jp='ap-northeast-1')
    TABLE_PREFIXS = dict(alpha='alpha', beta='beta', product='ipc')

    table_user_devices = '{0}.device-owner'.format(TABLE_PREFIXS[MONITOR_TYPE])
    table_devices = '{0}.device.info'.format(TABLE_PREFIXS[MONITOR_TYPE])
    table_account = '{0}.sso_account'.format(TABLE_PREFIXS[MONITOR_TYPE])


    for sr, lr in REGIONS.items():
        r = region.query.filter_by(regionshort=sr).first()
        if r == None:
            r = region(sr, lr)
            db.session.add(r)
        try:
            dynamodb = boto.dynamodb2.connect_to_region(REGIONS[sr])
        except Exception, e:
            continue

        # user devices counting
        try:
            table_user_result = dynamodb.scan(table_user_devices)
            
            user_devices = collections.defaultdict(int)
            for ownership in table_user_result.get('Items'):
                user_id = ownership['user_id']['S']
                user_devices[user_id] += 1

            device_users = collections.defaultdict(int)
            for user_id, devices in user_devices.items():
                device_users[devices] += 1

            for item in device_users.items():
                udtypename = 'User has ' +  str(item[0]) + ' device(s)'
                udct = counttype.query.\
                    filter_by(counttypename=udtypename).first()
                if udct == None:
                    udct = counttype(udtypename)
                    db.session.add(udct)

                ud_count_record = count.query.filter_by(clock=timefrom, \
                    region=r, counttype=udct).first()
                if ud_count_record != None:
                    ud_count_record.value = item[1]
                else:
                    ud_count_record = count(item[1], timefrom, r, udct)
                db.session.add(ud_count_record)

        except Exception, e:
            pass

        try:
            dev_model_result = dynamodb.scan(table_devices)
            devices = collections.defaultdict(int)
            for device in dev_model_result.get('Items'):
                if 'model' in device:
                    model = device['model']['S'].split()[0]
                    devices[model] += 1
            
            total_device_count = 0
            for item in devices.items():
                mtypename = item[0]
                mct = counttype.query.\
                    filter_by(counttypename=mtypename).first()
                if mct == None:
                    mct = counttype(mtypename)
                    db.session.add(mct)

                m_count_record = count.query.filter_by(clock=timefrom, \
                    region=r, counttype=mct).first()
                if m_count_record != None:
                    m_count_record.value = item[1]
                else:
                    m_count_record = count(item[1], timefrom, r, mct)
                db.session.add(m_count_record)

                total_device_count += item[1]

            ttypename = 'Total device count'
            tct = counttype.query.filter_by(counttypename=ttypename).first()
            if tct == None:
                tct = counttype(ttypename)
                db.session.add(tct)
            t_count_record = count.query.filter_by(clock=timefrom, \
                region=r, counttype=tct).first()
            if t_count_record != None:
                t_count_record.value = total_device_count
            else:
                t_count_record = count(total_device_count, timefrom, r, tct)
            db.session.add(t_count_record)
        except Exception, e:
            pass

        try:
            reg_user_result = dynamodb.scan(table_account)
            total_user_count = len(reg_user_result.get('Items'))
            tutypename = 'Total user count'
            tuct = counttype.query.filter_by(counttypename=tutypename).first()
            if tuct == None:
                tuct = counttype(tutypename)
                db.session.add(tuct)
            tu_count_record = count.query.filter_by(clock=timefrom, \
                region=r, counttype=tuct).first()
            if tu_count_record != None:
                tu_count_record.value = item[1]
            else:
                tu_count_record = count(total_user_count, timefrom, r, tuct)
            db.session.add(tu_count_record)
        except Exception, e:
            pass


        db.session.commit()


if __name__ == '__main__':
    update()
    update_counts()




                





