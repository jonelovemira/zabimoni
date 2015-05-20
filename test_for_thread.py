#! flask/bin/python

from monitor.decorators import async
from monitor.zabbix.models import Zabbixhistory,Zabbixhistoryuint
import json,time

@async
def test_for_multithread(item_arr):
	time_till = int(time.time())
	time_since = 0
	result = Zabbixhistory.get_update_history(item_arr,60,time_since,time_till)
	print item_arr,result


if __name__ == '__main__':
	item_arr_list = [[41026,41027]]
	for item_arr in item_arr_list:
		test_for_multithread(item_arr)

