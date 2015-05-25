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

    def gen_bhd_dict(self):
        
        service_metrics = {}

        for s in Service.query.all():
            service_metrics[s.servicename] = []
            for it in s.itemtypes.all():
                if it.condition is not None:
                    tmp = {'metricname': it.itemkey, 'condition': \
                        it.condition}
                    service_metrics[s.servicename].append(tmp)

        time_to = int(time.time())
        time_from = time_to - VALID_DAY_INTERVAL

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

        result['web']['INTERNAL_SUM_QCODESCANNED'] = {
            'time_from': 0,
            'time_to': time_to,
            'frequency': 60
        }

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
        return ''

    def business_health_test(self):
        return ''

    def core_data_test(self):
        return ''