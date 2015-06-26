#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor, config

from config import BY_GROUP_RESULT
from monitor import db
from monitor.odata.models import *
from monitor.chart.indextable import *
from monitor.chart.displaychart import Chart
from monitor.functions import gen_operational_itemtype
import time

DAY_INTERVAL = 86400
SUM_INDEX = 5



def update():
    itindex = gen_operational_itemtype()
    now = int(time.time())
    timeto = now // DAY_INTERVAL * DAY_INTERVAL
    timefrom = timeto - DAY_INTERVAL
    beginclock = timeto - ((time.gmtime(timeto).tm_mday - 1) * DAY_INTERVAL)

    om = odmonth.query.filter_by(beginclock=beginclock).first()
    if om is None:
        om = odmonth(beginclock)
        db.session.add(om)

    for itobj in itindex:
        history = intervaldata.query.filter_by(timefrom=timefrom, \
            timeto=timeto,groupname=itobj["groupname"], \
            itemkey=itobj["itemkey"]).all()
        print history
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
            itvd = intervaldata(timefrom, timeto, itobj["groupname"], \
                itobj["itemkey"], itobj["displayname"], vals[0][SUM_INDEX], om)
            db.session.add(itvd)

    db.session.commit()

if __name__ == '__main__':
    update()




                




