#!flask/bin/python
import os
import unittest

import json

from config import basedir
from monitor import app, db
from monitor.auth.models import User
from monitor.chart.models import *
from monitor.item.models import *
# from sqlalchemy import MetaData,create_engine,Table,Column,Integer,BigInteger,DateTime,Float
from monitor.zabbix import *
from monitor.chart.functions import *
# from monitor.item.functions import add_host,get_add_host_itemtype
from monitor.zabbix_api import zabbix_api
from prepare_env import init_aws_item,init_area,init_service,init_itemdatatype,init_normalitemtype,\
                        init_zbxitemtype,init_itemtype,mass_add_host_item_for_area

# from monitor.add_aws import add_aws,add_itemtype,get_zabbix_server_ip,add_aws_item

from coverage import coverage
cov = coverage(branch=True,omit=['flask/*','tests.py'])
cov.start()


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/newtest'
        self.app = app.test_client()
        db.session.remove()
        db.create_all()

        

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_generate_infile(self):
        save_json = 'xzy'
        generate_infile(save_json)
        f = open('monitor/static/js/export/generate/infile.json','r')
        x = f.read()
        f.close()
        assert save_json == x

    def test_generate_callback_js(self):
        generate_callback_js()
        callback_str = '''function(chart) {}'''
        f = open('monitor/static/js/export/generate/callback.js','r')
        result = f.read()
        f.close()
        # print result
        assert callback_str == result

    def test_generate_report_series_data(self):
        r = Report(600,1,'test report',None)
        db.session.add(r)
        s = Series('seriesname',0,'','','','',None,None,r)
        db.session.add(s)
        it1 = Itemtype('it1','it1')
        db.session.add(it1)
        i1 = Item(37277,'i1',None,it1)
        i2 = Item(37278,'i2',None,it1)
        db.session.add(i1)
        db.session.add(i2)

        db.session.add(s.add_item(i1))
        db.session.add(s.add_item(i2))

        db.session.commit()

        result = generate_report_series_data(r,1416383477,1416386957)
        assert len(result) != 0

    def test_generate_report_y_title(self):
        r = Report(600,1,'test report',None)
        db.session.add(r)
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        it2 = Itemtype('it2','it2',None,None,'Count',None)
        db.session.add(it1)
        db.session.add(it2)
        s1 = Series('seriesname1',0,'','','','',it1,None,r)
        s2 = Series('seriesname2',0,'','','','',it2,None,r)
        db.session.add(s1)
        db.session.add(s2)

        db.session.commit()

        res = generate_report_y_title(r)

        assert res == 'Percent,Count'

    def test_generate_report(self):
        u = User('root','root',0,1,'root@test.com')
        db.session.add(u)

        r = Report(600,1,'test report',u)
        db.session.add(r)
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)
        s = Series('seriesname',0,'','','','',it1,None,r)
        db.session.add(s)
        
        i1 = Item(37277,'i1',None,it1)
        i2 = Item(37278,'i2',None,it1)
        db.session.add(i1)
        db.session.add(i2)

        db.session.add(s.add_item(i1))
        db.session.add(s.add_item(i2))

        db.session.commit()

        # generate_report(r,'test',1416383477,1416386957)

    def test_get_all_itemtypes(self):
        # print 'process aws'
        # init_aws_item()
        # print 'process area'
        # init_area()
        # print 'process service'
        # init_service()
        # print 'process itemdatatype'
        # init_itemdatatype()
        # print 'process normalitemtype'
        # init_normalitemtype()
        # print 'process zbxitemtype'
        # init_zbxitemtype()
        # print 'process itemtype'
        # init_itemtype()
        # print 'process host item'

        # mass_add_host_item_for_area('ap-southeast-1')

        # get_all_itemtypes([1],[],[],[])
        get_all_itemtypes([],[],[],[])

    def test_init_history_data(self):
        item_arr=[37277,37278]
        init_history_data(item_arr)

    def test_update_history_data(self):
        item_arr = [37277,37278]
        time_till = 1416386957
        time_since = 1416383477
        update_history_data(item_arr,time_till,time_since)

    

    def test_arg_2_array(self):
        area = '12@2@4'
        assert arg_2_array(area) == ['12','2','4']

        service = '11@13'

        host = ''
        assert arg_2_array(host) == []
        
        aws = '15'
        result = index_arg_2_array(area,service,host,aws)
        assert result['area'] == ['12','2','4']
        assert result['service'] == ['11','13']
        assert result['host'] == []
        assert result['aws'] == ['15']

    def test_get_series_info(self):
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)

        s = Series('seriesname',0,'','','','',it1,None,None)
        db.session.add(s)
        
        i1 = Item(37277,'i1',None,it1)
        i2 = Item(37278,'i2',None,it1)
        db.session.add(i1)
        db.session.add(i2)

        db.session.add(s.add_item(i1))
        db.session.add(s.add_item(i2))

        db.session.commit()
        res = get_series_info([s])

    def test_str_2_seconds(self):
        strtime = '10/10/1989 11:20:03 PM'
        res = str_2_seconds(strtime)

    def test_save_report(self):
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)

        i = Item(37277,'i1',None,it1)
        db.session.add(i)
        reportname = 'r1'
        seriesinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"48","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        scaletype = 600
        functiontype = 1
        u = User('root','root',0,1,'root@test.com')
        db.session.add(u)
        save_report(reportname,seriesinfo,scaletype,functiontype,u,'','')
        db.session.commit()

    def test_update_series_data(self):
        update_data = []
        data = []
        s_s = 1416383477
        functiontype = 1
        update_series_data(update_data,data,s_s,functiontype)
        assert update_data[1] == None
        update_data = []
        data = [[1,0.2]]
        s_s = 1416383477
        functiontype = 1
        update_series_data(update_data,data,s_s,functiontype)
        assert update_data[1] == 0.2

    def test_get_init_y_title(self):
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)
        seriesinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"1","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        res = get_init_y_title(json.loads(seriesinfo)['current_series_info'])
        assert res == 'Percent'

    def test_init_result(self):
        sinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"1","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        seriesinfo = json.loads(sinfo)['current_series_info']
        time_frequency = '60'
        res = init_result(seriesinfo,time_frequency)
        assert len(res) != 0

    def test_update_result(self):
        sinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"1","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        seriesinfo = json.loads(sinfo)['current_series_info']
        time_frequency = '60'
        time_till = 1416386957
        res = update_result([seriesinfo],time_frequency,time_till)
        assert len(res) != 0

    def test_gen_new_cron(self):
        frequency = '86400'
        start_time = '12:20'
        esid = 3
        timezone = '8'
        res = gen_new_cron(frequency,start_time,esid,timezone)
        # print res
        assert res == '20 4 */1 * * /home/jone/flask_project/monitor-0.3.7/generate_report.py 3\n'

    def test_save_emailschedule(self):
        subject = ''
        reportids = {'report_id_list':[]}
        email = []
        frequency = '86400'
        start_time = '12:20'
        # esid = 3
        timezone = '8'
        owner = None
        save_emailschedule(subject,reportids,email,frequency,start_time,owner,timezone)
        db.session.commit()

        readfile = open('new.cron','r')
        res = readfile.read()
        readfile.close()
        print res
        assert res == '20 4 */1 * * /home/jone/flask_project/monitor-0.3.7/generate_report.py 1\n'


    def test_delete_schedule(self):
        try:
            delete_schedule(1)
        except Exception, e:
            pass

        count = Emailschedule.query.count()
        assert count == 0

        subject = ''
        reportids = {'report_id_list':[]}
        email = []
        frequency = '86400'
        start_time = '12:20'
        # esid = 3
        timezone = '8'
        owner = None
        save_emailschedule(subject,reportids,email,frequency,start_time,owner,timezone)

        count = Emailschedule.query.count()
        assert count == 1

        try:
            delete_schedule(1)
        except Exception, e:
            pass

        count = Emailschedule.query.count()
        assert count == 0

    def test_gen_report_img(self):

        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)

        i = Item(37277,'i1',None,it1)
        db.session.add(i)
        reportname = 'r1'
        seriesinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"1","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        scaletype = 600
        functiontype = 1
        u = User('root','root',0,1,'root@test.com')
        db.session.add(u)
        save_report(reportname,seriesinfo,scaletype,functiontype,u,'','')

        r = Report.query.first()

        subject = ''
        reportids = {'report_id_list':[1]}
        email = []
        frequency = '86400'
        start_time = '12:20'
        # esid = 3
        timezone = '8'
        owner = None
        save_emailschedule(subject,reportids,email,frequency,start_time,owner,timezone)
        db.session.commit()

        es = Emailschedule.query.first()
        # print es.reports.all()


        gen_report_img(1)

    def test_send_schedule_data(self):
        res = send_schedule_data()
        print res
        assert res == '[]'

    def test_send_specific_schedule(self):
        it1 = Itemtype('it1','it1',None,None,'Percent',None)
        db.session.add(it1)

        i = Item(37277,'i1',None,it1)
        db.session.add(i)
        reportname = 'r1'
        seriesinfo = '''{"current_series_info":[{"area_list":"","service_list":"","host_list":"10449","aws_list":"","series_type":"1","series_item_list":["37277"],"series_name":"host:192.168.221.130**Processor load (15 min average per core)"}]}'''
        scaletype = 600
        functiontype = 1
        u = User('root','root',0,1,'root@test.com')
        db.session.add(u)
        save_report(reportname,seriesinfo,scaletype,functiontype,u,'','')

        r = Report.query.first()

        subject = ''
        reportids = {'report_id_list':[1]}
        email = []
        frequency = '86400'
        start_time = '12:20'
        # esid = 3
        timezone = '8'
        owner = None
        save_emailschedule(subject,reportids,email,frequency,start_time,owner,timezone)
        db.session.commit()

        es = Emailschedule.query.first()
        gen_report_img(1)
        send_specific_schedule(1)

    def test_save_update_window_chart(self):

        print 'process aws'
        init_aws_item()
        print 'process area'
        init_area()
        print 'process service'
        init_service()
        print 'process itemdatatype'
        init_itemdatatype()
        print 'process normalitemtype'
        init_normalitemtype()
        print 'process zbxitemtype'
        init_zbxitemtype()
        print 'process itemtype'
        init_itemtype()
        print 'process host item'

        mass_add_host_item_for_area('ap-southeast-1')

        owner = User('root','root',0,1,'root@test.com')
        db.session.add(owner)
        wc_name = 'new window'
        current_series = [{u'service_list': u'', u'series_type': u'49', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (1 min average per core)', u'series_item_list': [u'37078']}, {u'service_list': u'', u'series_type': u'48', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (15 min average per core)', u'series_item_list': [u'37077']}]
        save_window_chart(wc_name,current_series,owner,wc_type=0,window_index=0,page=None)
        w1 = Window.query.first()
        assert len(w1.window_series.all()) == 2

        assert w1.window_series.first().items.count() == 1
        current_series = [{u'service_list': u'', u'series_type': u'49', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (1 min average per core)', u'series_item_list': [u'37078']}]
        update_window_chart(wc_name,current_series,owner)
        assert len(w1.window_series.all()) == 1

    def test_save_page_chart(self):
        print 'process aws'
        init_aws_item()
        print 'process area'
        init_area()
        print 'process service'
        init_service()
        print 'process itemdatatype'
        init_itemdatatype()
        print 'process normalitemtype'
        init_normalitemtype()
        print 'process zbxitemtype'
        init_zbxitemtype()
        print 'process itemtype'
        init_itemtype()
        print 'process host item'

        mass_add_host_item_for_area('ap-southeast-1')

        user = User('root','root',0,1,'root@test.com')
        db.session.add(user)

        pagename = 'new page'
        print '_'*10 + "save page chart" + '_'*10
        current_series = [{u'service_list': u'', u'series_type': u'49', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (1 min average per core)', u'series_item_list': [u'37078']}, {u'service_list': u'', u'series_type': u'48', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (15 min average per core)', u'series_item_list': [u'37077']}]
        series_info = [current_series]
        save_page_chart(pagename,series_info,user)
        current_series = [{u'service_list': u'', u'series_type': u'49', u'host_list': u'10450', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:relay-beta**Processor load (1 min average per core)', u'series_item_list': [u'37078']}]
        series_info = [current_series]
        update_page_chart(pagename,series_info,user)
        db.session.commit()



    

    # def test_report_init_result(self):
    #     current_series_info = [{u'service_list': u'', u'series_type': u'13', u'host_list': u'10413', u'aws_list': u'', u'area_list': u'',u'series_name': u'host:192.168.221.133<br/>CPU system time', u'series_item_list': [u'35485']}]
    #     time_frequency = u'600'
    #     time_since = u'10/14/2014 4:14:34 PM'
    #     time_till = u'11/04/2014 4:14:37 PM'
    #     result = report_init_result(current_series_info,time_frequency,time_since,time_till)
    #     print result
    #     assert len(result[0]['data']) != 0

    # def test_save_report(self):
    

    # def test_generate_report_series_data(self):
    #     reportid = 7
    #     generate_report_series_data(reportid);

    

    # def test_update_result(self):
    #     series_info = [[{u'service_list': u'', u'series_type': u'23', u'host_list': u'10415', u'aws_list': u'', u'area_list': u'', u'series_name': u'host:192.168.221.130**Context switches per second', u'series_item_list': [u'35532']}]]
    #     time_frequency = u'60'
    #     time_till = u'1415179427'
    #     result = update_result(series_info,time_frequency,time_till)
    #     assert len(result) == 1
    #     assert len(result[0]) == 1
    #     assert len(result[0][0]) == 2
    #     print result[0][0][1]
    #     assert result[0][0][0] == 1415179320000

# add_aws,add_itemtype,get_zabbix_server_ip,add_aws_item
    # def test_add_aws_item(self):
    #     area = Area(areaname='1')
    #     db.session.add(area)
    #     a = Aws(awsname='By All',area=area)
    #     db.session.add(a)
    #     add_aws_item()
    #     items = Item.query.all()
    #     assert len(items) != 0

    # def test_add_host(self):
    #     hostname = '192.168.221.130'
    #     host_ip = '192.168.221.130'
    #     zabbix = zabbix_api('192.168.221.130')
    #     s = Service(servicename='tests')
    #     db.session.add(s)
    #     a = Area(areaname='a')
    #     db.session.add(a)
    #     hostid = add_host(hostname, 'tests',host_ip,'a')
    #     assert hostid != None
    #     zabbix.host_delete([hostid])

    # def test_get_add_host_itemtype(self):
    #     get_add_host_itemtype()






if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "HTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()
    # unittest.main()