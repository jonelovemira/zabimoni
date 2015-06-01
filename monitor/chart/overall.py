import json, time
from monitor.chart.search import ItemSearch
from monitor.item.models import Service, Item, Host, Itemtype
from monitor.zabbix.models import Zabbixinterface, loadSession, Zabbixhosts, \
    Zabbixhistory, Zabbixhistoryuint
from monitor.chart.displaychart import Chart
from monitor.chart.indextable import RowContentGeneratorFactory

from config import CORE_BCD_TYPE, BY_GROUP_RESULT, PER_INSTANCE_RESULT

VALID_DAY_INTERVAL = 86400
VALID_MINUTE_INTERVAL = 60

class Overall():
    """docstring for Overall"""
    def __init__(self, arg):
        self.arg = arg
        self.info = []


    def overall_data(self,input_json):
        pass


    def gen_mhd_dict(self):
        services_data = []
        for s in Service.query.all():
            services_data.append(s.servicename)

        metrics_data = [{'metricname':'CPU idle time'},\
            {'metricname':'Available memory'},\
            {'metricname':'net.if.in[eth0]'},\
            {'metricname':'net.if.out[eth0]'}]

        time_to = int(time.time())
        time_from = time_to - VALID_DAY_INTERVAL

        result = {
            'services' : services_data,
            'metrics' : metrics_data,
            'time_to' : time_to,
            'time_from' : time_from
        }

        return result


    def gen_s2s_dict(self):
        its = Itemtype.query.filter(Itemtype.itemtypename.like('%@%')).all()
        data = []
        for it in its:
            tmp = {}
            name = it.itemtypename
            ft = name.split('_')[0]
            direction_tag = ft.split('@')[0]
            domain_tag = ft.split('@')[1]
            service = it.service.first()
            if service is not None:
                servicename = service.servicename

                tmp['servicename'] = servicename
                tmp['metricname'] = it.itemkey
                tmp['alias'] = it.itemtypename
                tmp[direction_tag] = domain_tag
                local_tag = 'FROM' if direction_tag == 'TO' else 'TO'
                # print direction_tag, local_tag, name
                assert direction_tag != local_tag
                tmp[local_tag] = servicename

                data.append(tmp)

        time_to = int(time.time())
        time_from = time_to - VALID_MINUTE_INTERVAL
        time_from = (time_from // VALID_MINUTE_INTERVAL) * VALID_MINUTE_INTERVAL

        result = {
            'data': data,
            'time_from': time_from,
            'time_to': time_to
        }
        
        return result

    def gen_bhd_dict(self, interval=None):
        
        service_metrics = {}

        for s in Service.query.all():
            service_metrics[s.servicename] = []
            for it in s.itemtypes.all():
                if it.condition is not None:
                    tmp = {'metricname': it.itemkey, 'condition': \
                        it.condition}
                    service_metrics[s.servicename].append(tmp)

        time_to = int(time.time())
        if interval is None:
            time_from = time_to - VALID_DAY_INTERVAL
        else:
            time_from = time_to - int(interval)

        result = {
            'service_metrics': service_metrics,
            'time_to':time_to,
            'time_from':time_from
        }

        return result

    def gen_cd_dict(self):
        
        result = {}

        time_to = int(time.time())
        time_from = time_to - VALID_DAY_INTERVAL

        for s in Service.query.all():
            result[s.servicename] = {}
            for it in s.itemtypes.all():
                if int(it.bcd_type) == CORE_BCD_TYPE:
                    result[s.servicename][it.itemkey] = {
                        'time_from': time_from,
                        'time_to': time_to,
                        'frequency': 60
                    }

        result['relay']['net.if.in[eth0]'] = {
            'time_from': time_from,
            'time_to': time_to,
            'frequency': 60
        }

        result['relay']['net.if.out[eth0]'] = {
            'time_from': time_from,
            'time_to': time_to,
            'frequency': 60
        }

        # result['web']['INTERNAL_SUM_QCODESCANNED'] = {
        #     'time_from': 0,
        #     'time_to': time_to,
        #     'frequency': 60
        # }

        return result


    '''
        input_dict = {'services': ['monitor'], 'metrics': [{'metricname':'us-east-1_AmazonEC2'}], 'time_to': 1428628814, 'time_from': 1428542432}
    '''
    def mechine_health(self,input_dict):
        services = input_dict['services']

        time_from = input_dict['time_from']
        time_to = input_dict['time_to']

        metrics = input_dict['metrics']
        session = loadSession()
        result = {}

        row_content_generator = RowContentGeneratorFactory()\
            .produce_generator(PER_INSTANCE_RESULT)

        assert row_content_generator != None, 'undefined row generator'

        for s in services:
            group = Service.query.filter_by(servicename=s).first()
            if group != None:
                result[s] = {}
                for h in group.hosts.all():
                    zinterface = session.query(Zabbixinterface).\
                        filter_by(hostid=h.hostid).first()
                    zh = session.query(Zabbixhosts).get(h.hostid)
                    if zinterface is None or zh is None:
                        continue
                    result[s][zinterface.ip] = {}
                    result[s][zinterface.ip]['available'] = zh.available

                    for m in metrics:
                        itemids = row_content_generator.content_2_id(\
                            row_content_generator.get_fake_row(zinterface.ip, \
                            m['metricname']))
                        # itemids = ItemSearch.find_item_list_for_table_row_instance([None,None,zinterface.ip,m['metricname'],None, None, None])

                        if len(itemids) > 0:
                            v = Zabbixhistory.get_interval_history_no_ground(\
                                    itemids,time_from,time_to)
                            vuint = Zabbixhistoryuint.\
                                get_interval_history_no_ground(\
                                itemids,time_from,time_to)
                            if vuint is  None and v is None:
                                continue
                            result[s][zinterface.ip][m['metricname']] = \
                                v if v is not None else vuint

        session.close()
        return result


    '''
    input = {'data':[{'FROM':'control', 'TO':'cas', 'metricname':\
    'TO@CAS_SUM_REQUEST', 'servicename': 'control', 'frequency':'60'}], \
    'time_from':1428628814, 'time_to': 1428542432}

    output = {'data':[{'FROM':'control', 'TO':'cas','metricname':\
        'TO@CAS_SUM_REQUEST', 'value':'10', 'servicename':'control'}],\
        'time_from':1428628814, 'time_to': 1428542432}
    '''
    def server_2_server_data(self, input_dict):


        time_from = input_dict['time_from']
        time_to = input_dict['time_to']

        data = input_dict['data']


        row_content_generator = RowContentGeneratorFactory()\
            .produce_generator(BY_GROUP_RESULT)

        assert row_content_generator != None, 'undefined row generator'

        session = loadSession()
        result = {}
        result['data'] = []
        for d in data:
            from_tag = d['FROM']
            to_tag = d['TO']
            servicename = d['servicename']
            metricname = d['metricname']
            ground = 60
            sm = servicename

            itemids = row_content_generator.content_2_id(\
                row_content_generator.get_fake_row(sm, metricname))

            if len(itemids) > 0:

                history_data = Chart.item_list_2_history_data(itemids,\
                    ground, time_from,time_to)
                series_data = Chart.\
                    item_history_data_2_chart_update_series_data(history_data,\
                    time_from, 1)
                last_sum = series_data[1]

                tmp = {
                    'FROM' : from_tag,
                    'TO' : to_tag,
                    'servicename': servicename,
                    'metricname': metricname,
                    'value': last_sum,
                    'alias':d['alias']
                }

                result['data'].append(tmp)



        result['time_from'] = input_dict['time_from']
        result['time_to'] = input_dict['time_to']
        session.close()

        return result

    '''input_dict =
    {'service_metrics':{'monitor':[{'metricname':'us-east-1_All','condition':'>100'}]},'time_from':1428451200,'time_to':1428624000}'''
    def business_health(self,input_dict):
        services_metrics = input_dict['service_metrics']

        time_from = input_dict['time_from']
        time_to = input_dict['time_to']

        session = loadSession()
        result = {}

        row_content_generator = RowContentGeneratorFactory()\
            .produce_generator(BY_GROUP_RESULT)

        assert row_content_generator != None, 'undefined row generator'

        for sm in services_metrics:
            group = Service.query.filter_by(servicename=sm).first()
            if group != None:
                result[sm] = []
                for metric_condition in services_metrics[sm]:
                    metricname = metric_condition['metricname']
                    condition = metric_condition['condition']
                    itemids = row_content_generator.content_2_id(\
                        row_content_generator.get_fake_row(sm, metricname))

                    if len(itemids) > 0:
                        recordsuint = Zabbixhistoryuint.\
                            get_interval_condition_record(itemids,\
                            time_from, time_to,condition)
                        records = Zabbixhistory.\
                            get_interval_condition_record(itemids,\
                            time_from, time_to, condition)

                        if records is None and recordsuint is None:
                            continue

                        tmp_records = recordsuint if recordsuint is not None \
                            else records

                        for r in tmp_records:
                            itemid = r[0]
                            clock = r[1]
                            value = r[2]
                            item = Item.query.get(itemid)
                            if item != None:
                                host = item.host
                                zinterface = session.query(Zabbixinterface).\
                                    filter_by(hostid=host.hostid).first()
                                if zinterface != None:
                                    result[sm].append([host.hostname, \
                                    zinterface.ip, item.itemname, clock, value])


        session.close()
        return result


    '''
    input: {'monitor':{'us-east-1_All':{'time_from':1428451200,'time_to':1428624000,'frequency':60}}}
    output: {'monitor': {'us-east-1_All': {'statics': [[6, 2462.3200000000002, 2799.8899999999999, 2129.0999999999999, 14773.92]], 'last': 2799.8899999999999}}}
    '''
    def core_data(self,input_dict):
        services_metrics = input_dict
        session = loadSession()
        result = {}

        row_content_generator = RowContentGeneratorFactory()\
            .produce_generator(BY_GROUP_RESULT)

        assert row_content_generator != None, 'undefined row generator'

        for sm in services_metrics:
            group = Service.query.filter_by(servicename=sm).first()
            if group != None:
                result[sm] = {}
                for metric in services_metrics[sm]:
                    time_from = services_metrics[sm][metric]['time_from']
                    time_to = services_metrics[sm][metric]['time_to']
                    ground = int(services_metrics[sm][metric]['frequency'])

                    result[sm][metric] = {}

                    itemids = row_content_generator.content_2_id(\
                        row_content_generator.get_fake_row(sm, metric))

                    # itemids = ItemSearch.find_item_list_for_table_row_group([sm,metric])

                    if len(itemids) > 0 :
                        v = Zabbixhistory.get_interval_history_no_ground(\
                            itemids, time_from, time_to)
                        vuint = Zabbixhistoryuint.\
                            get_interval_history_no_ground(itemids, \
                            time_from, time_to)

                        if vuint is  None and v is None:
                            continue

                        result[sm][metric]['statics'] = v if v is not None \
                            else vuint

                        time_from = time_to - ground
                        time_from = (time_from//ground) * ground

                        history_data = Chart.item_list_2_history_data(itemids, \
                            ground, time_from, time_to)
                        series_data = Chart.\
                            item_history_data_2_chart_update_series_data(\
                            history_data, time_from, 1)
                        last_sum = series_data[1]

                        result[sm][metric]['last'] = last_sum

        session.close()
        return result


    def server_2_server_data_test(self):
        return ''

    def mechine_health_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": {"10.2.64.21": {"available": 1, "net.if.out[eth0]": [[1440, 2022.8943999999999, 2696.0, 1848.0, 2912968.0]], "Available memory": [[1440, 482014802.48890001, 482103296.0, 480808960.0, 694101315584.0]], "CPU idle time": [[1440, 99.731305759999998, 99.849900000000005, 97.419200000000004, 143613.0803]], "net.if.in[eth0]": [[1440, 1690.8, 3208.0, 1544.0, 2434752.0]]}}, "web": {"10.2.72.29": {"available": 1, "net.if.out[eth0]": [[1440, 5646.8944000000001, 986336.0, 3088.0, 8131528.0]], "Available memory": [[1440, 543282173.15559995, 554160128.0, 498761728.0, 782326329344.0]], "CPU idle time": [[1440, 99.821791180000005, 99.883099999999999, 98.631500000000003, 143743.3793]], "net.if.in[eth0]": [[1440, 4034.75, 996848.0, 2440.0, 5810040.0]]}}, "gdbs": {"10.2.108.45": {"available": 1, "net.if.out[eth0]": [[1439, 2617.6233000000002, 3536.0, 1760.0, 3766760.0]], "Available memory": [[1440, 684315064.88890004, 684544000.0, 682991616.0, 985413693440.0]], "CPU idle time": [[1435, 99.46100878, 99.7483, 98.011399999999995, 142726.54759999999]], "net.if.in[eth0]": [[1439, 2118.4322000000002, 2856.0, 1448.0, 3048424.0]]}}, "monitor": {"10.2.0.253": {"available": 1}}, "relay": {"10.2.89.11": {"available": 1, "net.if.out[eth0]": [[1430, 5178.607, 6104.0, 3600.0, 7405408.0]], "Available memory": [[1430, 325689790.83639997, 326672384.0, 324599808.0, 465736400896.0]], "CPU idle time": [[1430, 96.804720140000001, 97.231899999999996, 84.929199999999994, 138430.74979999999]], "net.if.in[eth0]": [[1430, 4048.6154000000001, 5008.0, 2720.0, 5789520.0]]}}, "cas": {"10.2.104.231": {"available": 1, "net.if.out[eth0]": [[1320, 2193.9636, 4680.0, 392.0, 2896032.0]], "Available memory": [[1320, 699825859.49090004, 704729088.0, 673095680.0, 923770134528.0]], "CPU idle time": [[1319, 99.746915009999995, 99.9833, 95.923100000000005, 131566.18090000001]], "net.if.in[eth0]": [[1320, 1818.3515, 3760.0, 296.0, 2400224.0]]}}, "unknown": {"10.2.88.102": {"available": 1, "net.if.out[eth0]": [[1440, 2286.7111, 3920.0, 2160.0, 3292864.0]], "Available memory": [[1440, 473569627.02219999, 474882048.0, 471756800.0, 681940262912.0]], "CPU idle time": [[1440, 99.668211670000005, 99.783199999999994, 95.784000000000006, 143522.2248]], "net.if.in[eth0]": [[1440, 1978.3722, 3472.0, 1880.0, 2848856.0]]}}, "ss": {}, "nat": {}, "push": {}, "dbs": {"10.2.101.102": {"available": 1, "net.if.out[eth0]": [[1440, 3676.0832999999998, 5872.0, 3336.0, 5293560.0]], "Available memory": [[1440, 357129136.3556, 357261312.0, 355946496.0, 514265956352.0]], "CPU idle time": [[1440, 99.476359369999997, 99.731800000000007, 98.031999999999996, 143245.95749999999]], "net.if.in[eth0]": [[1440, 2782.2833000000001, 4160.0, 2520.0, 4006488.0]]}}, "stun": {"10.2.96.244": {"available": 1, "net.if.out[eth0]": [[1440, 3304.4389000000001, 4576.0, 3184.0, 4758392.0]], "Available memory": [[1440, 536415812.26670003, 536604672.0, 534712320.0, 772438769664.0]], "CPU idle time": [[1440, 98.139177219999993, 98.266099999999994, 93.921700000000001, 141320.41519999999]], "net.if.in[eth0]": [[1440, 2596.6667000000002, 4656.0, 2504.0, 3739200.0]]}}}}'''

    def business_health_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": [], "web": [["web-alpha", "10.2.72.29", "TO@CAS_SUM_TIMEOUT", 1432518961, 1], ["web-alpha", "10.2.72.29", "TO@CAS_SUM_REQ_ERR_COUNT", 1432518961, 1]], "gdbs": [], "monitor": [], "relay": [], "cas": [], "unknown": [], "ss": [], "nat": [], "push": [], "dbs": [], "stun": []}}'''

    def core_data_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": {"CloudRequest": {"statics": [[1440, 3.8742999999999999, 5.0, 3.0, 5579.0]], "last": 4.0}, "OnlineDevice": {"statics": [[1440, 2.0, 2.0, 2.0, 2880.0]], "last": 2.0}}, "web": {"FROM-WEB_SUM_REQUEST": {"statics": [[1440, 0.0035000000000000001, 5.0, 0.0, 5.0]], "last": 0.0}, "FROM-ANDROID_SUM_REQUEST": {"statics": [[1440, 0.0, 0.0, 0.0, 0.0]], "last": 0.0}, "FROM-IOS_SUM_REQUEST": {"statics": [[1440, 0.0, 0.0, 0.0, 0.0]], "last": 0.0}}, "gdbs": {}, "monitor": {}, "relay": {"FROM-CLIENT_SUM_POST": {"statics": [[1440, 1.0187999999999999, 2.0, 1.0, 1467.0]], "last": 1.0}, "net.if.in[eth0]": {"statics": [[1440, 13178.022199999999, 613136.0, 3808.0, 18976352.0]], "last": 3992.0}, "FROM-CLIENT_SUM_GET": {"statics": [[1440, 0.058299999999999998, 7.0, 0.0, 84.0]], "last": 0.0}, "net.if.out[eth0]": {"statics": [[1440, 31252.25, 2929544.0, 4960.0, 45003240.0]], "last": 5096.0}}, "cas": {}, "unknown": {}, "ss": {}, "nat": {}, "push": {}, "dbs": {}, "stun": {}}}'''