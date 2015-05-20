import json, time
from monitor.chart.search import ItemSearch
from monitor.item.models import Service, Item, Host, Itemtype
from monitor.zabbix.models import Zabbixinterface, loadSession, Zabbixhosts, \
    Zabbixhistory, Zabbixhistoryuint
from monitor.chart.displaychart import Chart

from config import CORE_BCD_TYPE

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

        metrics_data = [{'metricname':'system.cpu.util[,idle]'},\
            {'metricname':'vm.memory.size[available]'},\
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
        for s in services:
            group = Service.query.filter_by(servicename=s).first()
            if group != None:
                result[s] = {}
                for h in group.hosts.all():
                    zinterface = session.query(Zabbixinterface).filter_by(hostid=h.hostid).first()
                    zh = session.query(Zabbixhosts).get(h.hostid)
                    if zinterface is None or zh is None:
                        continue
                    result[s][zinterface.ip] = {}
                    result[s][zinterface.ip]['available'] = zh.available

                    for m in metrics:
                        itemids = ItemSearch.find_item_list_for_table_row_instance([None,None,zinterface.ip,m['metricname']])

                        if len(itemids) > 0:
                            v = Zabbixhistory.get_interval_history_no_ground(itemids,time_from,time_to)
                            vuint = Zabbixhistoryuint.get_interval_history_no_ground(itemids,time_from,time_to)
                            if vuint is  None and v is None:
                                continue
                            result[s][zinterface.ip][m['metricname']] = v if v is not None else vuint

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
            itemids = ItemSearch.find_item_list_for_table_row_group([sm,metricname])
            if len(itemids) > 0:

                history_data = Chart.item_list_2_history_data(itemids,ground,time_from,time_to)
                series_data = Chart.item_history_data_2_chart_update_series_data(history_data,time_from,1)
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

        for sm in services_metrics:
            group = Service.query.filter_by(servicename=sm).first()
            if group != None:
                result[sm] = []
                for metric_condition in services_metrics[sm]:
                    metricname = metric_condition['metricname']
                    condition = metric_condition['condition']
                    itemids = ItemSearch.find_item_list_for_table_row_group([sm,metricname])

                    if len(itemids) > 0:
                        recordsuint = Zabbixhistoryuint.get_interval_condition_record(itemids,time_from,time_to,condition)
                        records = Zabbixhistory.get_interval_condition_record(itemids,time_from,time_to,condition)
                        if records is None and recordsuint is None:
                            continue
                        tmp_records = recordsuint if recordsuint is not None else records
                        for r in tmp_records:
                            itemid = r[0]
                            clock = r[1]
                            value = r[2]
                            item = Item.query.get(itemid)
                            if item != None:
                                host = item.host
                                zinterface = session.query(Zabbixinterface).filter_by(hostid=host.hostid).first()
                                if zinterface != None:
                                    result[sm].append([host.hostname,zinterface.ip,item.itemname,clock,value])


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
        for sm in services_metrics:
            group = Service.query.filter_by(servicename=sm).first()
            if group != None:
                result[sm] = {}
                for metric in services_metrics[sm]:
                    time_from = services_metrics[sm][metric]['time_from']
                    time_to = services_metrics[sm][metric]['time_to']
                    ground = int(services_metrics[sm][metric]['frequency'])

                    result[sm][metric] = {}

                    itemids = ItemSearch.find_item_list_for_table_row_group([sm,metric])

                    if len(itemids) > 0 :
                        v = Zabbixhistory.get_interval_history_no_ground(itemids,time_from,time_to)
                        vuint = Zabbixhistoryuint.get_interval_history_no_ground(itemids,time_from,time_to)
                        if vuint is  None and v is None:
                            continue

                        result[sm][metric]['statics'] = v if v is not None else vuint

                        time_from = time_to - ground
                        time_from = (time_from//ground) * ground

                        history_data = Chart.item_list_2_history_data(itemids,ground,time_from,time_to)
                        series_data = Chart.item_history_data_2_chart_update_series_data(history_data,time_from,1)
                        last_sum = series_data[1]

                        result[sm][metric]['last'] = last_sum

        session.close()
        return result


    def server_2_server_data_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"time_to": 1431065446, "time_from": 1431065340, "data": [{"FROM": "control", "TO": "CAS", "value": 2.0, "alias": "TO@CAS_SUM_REQUEST", "servicename": "control", "metricname": "CASRequest"}, {"FROM": "control", "TO": "DBS", "value": 0.0, "alias": "TO@DBS_SUM_REQUEST", "servicename": "control", "metricname": "DBSRequest"}, {"FROM": "control", "TO": "LOCAL", "value": 2.0, "alias": "TO@LOCAL_SUM_REQUEST", "servicename": "control", "metricname": "LocalRequest"}, {"FROM": "OTHER", "TO": "cas", "value": null, "alias": "FROM@OTHER_SUM_REQCOUNT", "servicename": "cas", "metricname": "FROM_OTHER_REQ"}, {"FROM": "WEB", "TO": "cas", "value": null, "alias": "FROM@WEB_SUM_REQCOUNT", "servicename": "cas", "metricname": "FROM_WEB_REQ"}, {"FROM": "cas", "TO": "CHCHE", "value": null, "alias": "TO@CHCHE_REQ_ERR_COUNT", "servicename": "cas", "metricname": "TO_CACHE_ERR"}, {"FROM": "cas", "TO": "DBS", "value": null, "alias": "TO@DBS_SUM_REQ_ERR_COUNT", "servicename": "cas", "metricname": "TO_DBS_ERR"}, {"FROM": "cas", "TO": "DBS", "value": null, "alias": "TO@DBS_SUM_REQCOUNT", "servicename": "cas", "metricname": "TO_DBS_REQ"}, {"FROM": "control", "TO": "CAS", "value": 0.0, "alias": "TO@CAS_SUM_ERROR", "servicename": "control", "metricname": "CASError"}, {"FROM": "control", "TO": "DBS", "value": 0.0, "alias": "TO@DBS_SUM_ERROR", "servicename": "control", "metricname": "DBSError"}, {"FROM": "CLIENT", "TO": "relay", "value": 6.0, "alias": "FROM@CLIENT_SUM_Conn", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_Conn"}, {"FROM": "CLIENT", "TO": "relay", "value": 2.0, "alias": "FROM@CLIENT_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET"}, {"FROM": "ANDROID", "TO": "relay", "value": 7.0, "alias": "FROM@ANDROID_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET_Android"}, {"FROM": "IOS", "TO": "relay", "value": 0.0, "alias": "FROM@IOS_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET_IOS"}, {"FROM": "MAC", "TO": "relay", "value": 0.0, "alias": "FROM@MAC_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET_MAC"}, {"FROM": "WINIE", "TO": "relay", "value": 0.0, "alias": "FROM@WINIE_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET_WINIE"}, {"FROM": "WINNONIE", "TO": "relay", "value": 0.0, "alias": "FROM@WINNONIE_SUM_GET", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_GET_WINNONIE"}, {"FROM": "CLIENT", "TO": "relay", "value": 1.0, "alias": "FROM@CLIENT_SUM_INVALIDHTTP", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_INVALIDHTTP"}, {"FROM": "CLIENT", "TO": "relay", "value": 3.0, "alias": "FROM@CLIENT_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST"}, {"FROM": "DUT200", "TO": "relay", "value": 0.0, "alias": "FROM@DUT200_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST_DUT200"}, {"FROM": "DUT220", "TO": "relay", "value": 1.0, "alias": "FROM@DUT220_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST_DUT220"}, {"FROM": "DUT250", "TO": "relay", "value": 0.0, "alias": "FROM@DUT250_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST_DUT250"}, {"FROM": "DUT350", "TO": "relay", "value": 0.0, "alias": "FROM@DUT350_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST_DUT350"}, {"FROM": "DUT450", "TO": "relay", "value": 0.0, "alias": "FROM@DUT450_SUM_POST", "servicename": "relay", "metricname": "FROM-CLIENT_SUM_POST_DUT450"}, {"FROM": "relay", "TO": "CAS", "value": 0.0, "alias": "TO@CAS_SUM_INVALID401", "servicename": "relay", "metricname": "TO-CAS_SUM_INVALID401"}, {"FROM": "relay", "TO": "CAS", "value": 4.0, "alias": "TO@CAS_SUM_INVALID404", "servicename": "relay", "metricname": "TO-CAS_SUM_INVALID404"}, {"FROM": "relay", "TO": "CAS", "value": 0.0, "alias": "TO@CAS_SUM_REQUEST", "servicename": "relay", "metricname": "TO-CAS_SUM_REQUEST"}, {"FROM": "relay", "TO": "CAS", "value": 4.0, "alias": "TO@CAS_SUM_REQUESTERROR", "servicename": "relay", "metricname": "TO-CAS_SUM_REQUESTERROR"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_Conn", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_Conn"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_Conn_Fail", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_Conn_Fail"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_Conn_Success", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_Conn_Success"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_NAT_FullCone", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_NAT_FullCone"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_NAT_IPCone", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_NAT_IPCone"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_NAT_Open", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_NAT_Open"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_NAT_PortCone", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_NAT_PortCone"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_NAT_Symetric", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_NAT_Symetric"}, {"FROM": "CLIENT", "TO": "stun", "value": 0.0, "alias": "FROM@CLIENT_SUM_Z_Count", "servicename": "stun", "metricname": "FROM-CLIENT_SUM_Z_Count"}, {"FROM": "ANDROID", "TO": "web", "value": 2.0, "alias": "FROM@ANDROID_SUM_REQCOUNT", "servicename": "web", "metricname": "FROM-ANDROID_SUM_REQUEST"}, {"FROM": "IOS", "TO": "web", "value": 9.0, "alias": "FROM@IOS_SUM_REQCOUNT", "servicename": "web", "metricname": "FROM-IOS_SUM_REQUEST"}, {"FROM": "WEBPAGE", "TO": "web", "value": 4.0, "alias": "FROM@WEBPAGE_SUM_REQCOUNT", "servicename": "web", "metricname": "FROM-WEB_SUM_REQUEST"}, {"FROM": "web", "TO": "CAS", "value": 16.0, "alias": "TO@CAS_SUM_REQCOUNT", "servicename": "web", "metricname": "TO-CAS_SUM_REQUEST"}, {"FROM": "web", "TO": "CAS", "value": 0.0, "alias": "TO@CAS_SUM_REQ_ERR_COUNT", "servicename": "web", "metricname": "TO-CAS_SUM_REQUESTERROR"}, {"FROM": "web", "TO": "CAS", "value": 0.0, "alias": "TO@CAS_SUM_TIMEOUT", "servicename": "web", "metricname": "TO-CAS_SUM_TIMEOUT"}, {"FROM": "web", "TO": "CTL", "value": 0.0, "alias": "TO@CTL_SUM_REQCOUNT", "servicename": "web", "metricname": "TO-CTL_SUM_REQUEST"}, {"FROM": "web", "TO": "CTL", "value": 0.0, "alias": "TO@CTL_SUM_REQ_ERR_COUNT", "servicename": "web", "metricname": "TO-CTL_SUM_REQUESTERROR"}, {"FROM": "web", "TO": "CTL", "value": 0.0, "alias": "TO@CTL_SUM_TIMEOUT", "servicename": "web", "metricname": "TO-CTL_SUM_TIMEOUT"}, {"FROM": "web", "TO": "DBS", "value": 13.0, "alias": "TO@DBS_SUM_REQCOUNT", "servicename": "web", "metricname": "TO-DBS_SUM_REQUEST"}, {"FROM": "web", "TO": "DBS", "value": 0.0, "alias": "TO@DBS_SUM_REQ_ERR_COUNT", "servicename": "web", "metricname": "TO-DBS_SUM_REQUESTERROR"}, {"FROM": "web", "TO": "DBS", "value": 0.0, "alias": "TO@DBS_SUM_TIMEOUT", "servicename": "web", "metricname": "TO-DBS_SUM_TIMEOUT"}]}}'''


    def mechine_health_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": {"10.2.64.21": {"available": 1, "system.cpu.util[,idle]": [[1440, 99.724605629999999, 99.833200000000005, 97.533699999999996, 143603.43210000001]], "vm.memory.size[available]": [[1440, 481848647.11110002, 481939456.0, 480612352.0, 693862051840.0]], "net.if.out[eth0]": [[1437, 2047.6659999999999, 3600.0, 1848.0, 2942496.0]], "net.if.in[eth0]": [[1438, 1709.7079000000001, 3424.0, 1536.0, 2458560.0]]}}, "web": {"10.2.73.185": {"available": 2}, "10.2.72.29": {"available": 1, "system.cpu.util[,idle]": [[1439, 99.827070469999995, 99.883200000000002, 98.7483, 143651.1544]], "vm.memory.size[available]": [[1440, 806596275.20000005, 820334592.0, 745959424.0, 1161498636288.0]], "net.if.out[eth0]": [[1438, 3366.0918000000001, 110528.0, 2904.0, 4840440.0]], "net.if.in[eth0]": [[1438, 2591.6106, 11256.0, 2280.0, 3726736.0]]}, "10.2.73.247": {"available": 2}, "10.2.72.242": {"available": 2}}, "gdbs": {"10.2.108.45": {"available": 1, "system.cpu.util[,idle]": [[1439, 99.429676229999998, 99.731399999999994, 98.246799999999993, 143079.30410000001]], "vm.memory.size[available]": [[1440, 687853576.53330004, 688177152.0, 686579712.0, 990509150208.0]], "net.if.out[eth0]": [[1438, 2567.6439, 4000.0, 1976.0, 3692272.0]], "net.if.in[eth0]": [[1438, 2081.0626000000002, 3208.0, 1720.0, 2992568.0]]}}, "monitor": {"10.2.5.183": {"available": 1}, "10.2.0.253": {"available": 1}}, "relay": {"10.2.89.11": {"available": 1, "system.cpu.util[,idle]": [[1438, 97.16788554, 97.800399999999996, 88.587599999999995, 139727.41940000001]], "vm.memory.size[available]": [[1439, 466168270.54339999, 477462528.0, 397377536.0, 670816141312.0]], "net.if.out[eth0]": [[1437, 4942.5357999999997, 36696.0, 3744.0, 7102424.0]], "net.if.in[eth0]": [[1437, 4643.9861000000001, 1135232.0, 2872.0, 6673408.0]]}, "10.2.88.87": {"available": 2}, "10.2.89.142": {"available": 2}}, "cas": {"10.2.104.91": {"available": 2}, "10.2.105.21": {"available": 2}, "10.2.104.196": {"available": 2}, "10.2.104.231": {"available": 1, "system.cpu.util[,idle]": [[1440, 99.72979583, 99.9833, 96.260800000000003, 143610.90599999999]], "vm.memory.size[available]": [[1438, 941809248.13349998, 949121024.0, 913395712.0, 1354321698816.0]]}, "10.2.104.234": {"available": 2}, "10.2.105.202": {"available": 2}, "10.2.104.4": {"available": 2}, "10.2.105.99": {"available": 2}}, "unknown": {"10.2.4.115": {"available": 2}, "10.2.4.21": {"available": 2}, "10.2.88.102": {"available": 1, "system.cpu.util[,idle]": [[1439, 99.649626819999995, 99.799800000000005, 95.635499999999993, 143395.81299999999]], "vm.memory.size[available]": [[1440, 452654492.44440001, 453791744.0, 450596864.0, 651822469120.0]], "net.if.out[eth0]": [[1436, 2261.5041999999999, 5752.0, 2040.0, 3247520.0]], "net.if.in[eth0]": [[1436, 1985.5376000000001, 10552.0, 1792.0, 2851232.0]]}}, "nat": {}, "push": {}, "dbs": {"10.2.101.102": {"available": 1, "system.cpu.util[,idle]": [[1439, 99.485323140000006, 99.731899999999996, 92.380499999999998, 143159.38]], "vm.memory.size[available]": [[1440, 500112256.0, 523288576.0, 385671168.0, 720161648640.0]], "net.if.out[eth0]": [[1437, 2974.9367000000002, 9088.0, 2368.0, 4274984.0]], "net.if.in[eth0]": [[1437, 3155.0452, 1122624.0, 1960.0, 4533800.0]]}}, "stun": {"10.2.96.244": {"available": 1, "system.cpu.util[,idle]": [[1439, 98.119851769999997, 98.265799999999999, 94.317599999999999, 141194.46669999999]], "vm.memory.size[available]": [[1439, 529120272.36690003, 529408000.0, 527896576.0, 761404071936.0]], "net.if.out[eth0]": [[1437, 3235.2512000000002, 4032.0, 2720.0, 4649056.0]], "net.if.in[eth0]": [[1437, 2546.8281000000002, 3568.0, 2128.0, 3659792.0]]}}}}'''

    def business_health_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": [["control-alpha", "10.2.64.21", "INTERNAL_SUM_ERROR", 1430793301, 1]], "web": [["web-alpha", "10.2.72.29", "TO@DBS_SUM_REQ_ERR_COUNT", 1430789761, 1]], "gdbs": [], "monitor": [], "relay": [["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430747161, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430751962, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430753581, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430753642, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430758802, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430760122, 2], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430765402, 12], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430777581, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430778001, 4], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430784602, 4], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430785201, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430788381, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430788442, 4], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430788741, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430794742, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430799122, 4], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430800381, 4], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430806202, 5], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430806381, 5], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430814361, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430815382, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430816282, 1], ["relay-alpha", "10.2.89.11", "FROM@CLIENT_SUM_INVALIDHTTP", 1430816342, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430731681, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430731742, 47], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430731802, 46], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430731922, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430731982, 35], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430732042, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430732101, 29], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430732162, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430732641, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733362, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733421, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733482, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733541, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733602, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733662, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733721, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733782, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733842, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733902, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430733962, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734021, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734082, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734141, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734202, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734261, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734321, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734382, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734441, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734562, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734621, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734682, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734742, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734801, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734862, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734922, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430734981, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735042, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735101, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735161, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735222, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735281, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735342, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735402, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735461, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735522, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735581, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735642, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430735701, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736301, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736362, 25], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736422, 34], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736481, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736601, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430736721, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737081, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737142, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737201, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737262, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737322, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737381, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737442, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737502, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737561, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737622, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737681, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737861, 33], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737921, 33], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430737982, 42], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430738041, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430738102, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430753761, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430786402, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430788681, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430791741, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430791803, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792162, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792221, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792402, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792461, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792522, 27], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792581, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792642, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792701, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792762, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792821, 6], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792882, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430792942, 49], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793001, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793062, 8], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793122, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793181, 29], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793242, 52], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793301, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793362, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793421, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793482, 9], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793722, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793782, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793841, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793902, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430793961, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794022, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794082, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794142, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794202, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794262, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794321, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794382, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794441, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794502, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794681, 36], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430794742, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795341, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795402, 35], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795461, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795522, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795581, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795642, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795822, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430795942, 9], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796001, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796062, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796121, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796182, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796241, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796302, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796362, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796421, 24], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796482, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796541, 40], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796602, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796662, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796721, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796782, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430796841, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797142, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797202, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797322, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797381, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797442, 24], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797501, 32], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797561, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797622, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797681, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797742, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797801, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797862, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430797921, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430804941, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805182, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805242, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805301, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805362, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805421, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805482, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430805541, 8], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430806742, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808602, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808721, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808782, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808841, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808902, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430808962, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430809022, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430809081, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430809142, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_INVALID404", 1430809202, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430731682, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430731743, 47], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430731803, 46], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430731923, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430731983, 35], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430732042, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430732102, 29], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430732163, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430732642, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733363, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733422, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733483, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733542, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733603, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733662, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733722, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733783, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733842, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733903, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430733963, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734022, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734083, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734142, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734203, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734263, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734322, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734383, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734442, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734563, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734622, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734683, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734743, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734802, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734863, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734923, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430734982, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735043, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735103, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735162, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735223, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735282, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735343, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735402, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735462, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735523, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735582, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735643, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430735702, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736302, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736363, 25], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736423, 34], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736482, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736602, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430736722, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737082, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737142, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737202, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737263, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737323, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737382, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737443, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737503, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737562, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737623, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737682, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737862, 33], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737922, 33], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430737982, 42], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430738042, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430738103, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430753762, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430786403, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430788682, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430791742, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430791803, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792162, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792222, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792403, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792462, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792523, 27], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792582, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792643, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792702, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792763, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792822, 6], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792883, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430792943, 49], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793002, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793063, 8], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793122, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793182, 29], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793243, 52], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793302, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793363, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793422, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793483, 9], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793723, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793783, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793842, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793903, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430793962, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794023, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794082, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794143, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794203, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794263, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794322, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794383, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794442, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794503, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794682, 36], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430794743, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795342, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795403, 35], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795462, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795523, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795582, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795643, 15], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795822, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430795942, 9], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796002, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796063, 21], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796122, 4], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796183, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796242, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796303, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796363, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796422, 24], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796483, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796542, 40], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796603, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796663, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796722, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796783, 17], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430796842, 22], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797143, 2], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797203, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797323, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797382, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797443, 24], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797502, 32], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797562, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797622, 10], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797682, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797742, 18], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797802, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797863, 13], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430797922, 11], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430804942, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805183, 7], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805243, 20], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805302, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805363, 19], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805422, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805483, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430805542, 8], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430806742, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808603, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808722, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808783, 14], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808842, 1], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808903, 12], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430808962, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430809023, 16], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430809082, 5], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430809143, 3], ["relay-alpha", "10.2.89.11", "TO@CAS_SUM_REQUESTERROR", 1430809203, 12]], "cas": [], "unknown": [], "nat": [], "push": [], "dbs": [], "stun": []}}'''

    def core_data_test(self):
        return '''{"get_result_bool": true, "info": "success", "get_result": {"control": {"CloudRequest": {"statics": [[1440, 5.9471999999999996, 37.0, 3.0, 8564.0]], "last": 6.0}, "OnlineDevice": {"statics": [[1440, 3.0507, 4.0, 2.0, 4393.0]], "last": 3.0}}, "web": {"INTERNAL_SUM_QCODESCANNED": {"statics": [[1609, 0.0, 0.0, 0.0, 0.0]], "last": 0.0}, "FROM-WEB_SUM_REQUEST": {"statics": [[1440, 0.015299999999999999, 11.0, 0.0, 22.0]], "last": 0.0}, "FROM-ANDROID_SUM_REQUEST": {"statics": [[1440, 0.1188, 14.0, 0.0, 171.0]], "last": 0.0}, "FROM-IOS_SUM_REQUEST": {"statics": [[1440, 0.022200000000000001, 8.0, 0.0, 32.0]], "last": 0.0}}, "gdbs": {}, "monitor": {}, "relay": {"FROM-CLIENT_SUM_POST": {"statics": [[1440, 20.0319, 86.0, 0.0, 28846.0]], "last": 86.0}, "net.if.in[eth0]": {"statics": [[1437, 4645.7897999999996, 1135232.0, 2872.0, 6676000.0]], "last": 3912.0}, "FROM-CLIENT_SUM_GET": {"statics": [[1440, 0.18190000000000001, 11.0, 0.0, 262.0]], "last": 0.0}, "net.if.out[eth0]": {"statics": [[1437, 4945.4141, 36696.0, 3744.0, 7106560.0]], "last": 5208.0}}, "cas": {}, "unknown": {}, "nat": {}, "push": {}, "dbs": {}, "stun": {}}}'''
