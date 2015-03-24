from monitor.item.models import Item,Host,Service,Itemtype,Zbxitemtype,Normalitemtype,Aws
from monitor.zabbix.models import Zabbixhosts,Zabbixinterface
from config import BY_GROUP_RESULT,PER_INSTANCE_RESULT,BY_GROUP_TABLE_HEAD,\
					TABLE_HEAD_GROUP_NAME,TABLE_HEAD_INSTANCE_NAME,TABLE_HEAD_IP,\
					TABLE_HEAD_METRIC_NAME,PER_INSTANCE_TABLE_HEAD,AWS_FEE_TABEL_HEAD,\
					NO_FEE_RESULT_SET


def by_group_name(row):
	return row[BY_GROUP_TABLE_HEAD.index(TABLE_HEAD_GROUP_NAME)] + ' ' + row[BY_GROUP_TABLE_HEAD.index(TABLE_HEAD_METRIC_NAME)]

def per_instance_name(row):
	return row[PER_INSTANCE_TABLE_HEAD.index(TABLE_HEAD_IP)] + ' ' + row[PER_INSTANCE_TABLE_HEAD.index(TABLE_HEAD_METRIC_NAME)]

def aws_fee_name(row):
	return row[AWS_FEE_TABEL_HEAD.index(TABLE_HEAD_METRIC_NAME)]


class BaseSearch():

	@classmethod
	def search(cls,search_object,filter_boolean):
		result = search_object.filter(filter_boolean).all()
		return result


		
class ItemSearch(BaseSearch):
	
	@classmethod
	def search(cls,filter_boolean):
		result = BaseSearch.search(Item.query,filter_boolean)
		return result

	@classmethod
	def generate_by_group_result_no_fee(cls,item_search_result,asg_name=None):
		result = {}
		table_head = BY_GROUP_TABLE_HEAD
		metric_count = 0
		metric_result = []
		for s in item_search_result:
			if s.itemtype.aws != None or s.itemtype.itemunit == None:
				continue

			if asg_name != None and s.host.service.servicename != asg_name:
				continue

			if [s.host.service.servicename,s.itemname] not in metric_result:
				metric_count += 1
				row = [s.host.service.servicename,s.itemname]
				assert len(row) == len(table_head)
				metric_result.append(row)

		result['table_head'] = table_head
		result['metric_count'] = metric_count
		result['metric_result'] = metric_result
		return result

	@classmethod
	def find_item_list_for_table_row_group(cls,row):
		result = []
		metric_name = row[BY_GROUP_TABLE_HEAD.index(TABLE_HEAD_METRIC_NAME)]
		service_name = row[BY_GROUP_TABLE_HEAD.index(TABLE_HEAD_GROUP_NAME)]
		filter_boolean = ItemSearchValue2Filter.parse(metric_name)
		search_result = cls.search(filter_boolean)
		for item in search_result:
			if item.host.service.servicename == service_name:
				result.append(item.itemid)

		return result

	@classmethod
	def find_item_list_for_table_row_instance(cls,row):
		result = []
		metric_name = row[PER_INSTANCE_TABLE_HEAD.index(TABLE_HEAD_METRIC_NAME)]
		ip = row[PER_INSTANCE_TABLE_HEAD.index(TABLE_HEAD_IP)]
		filter_boolean = ItemSearchValue2Filter.parse(metric_name)
		search_result = cls.search(filter_boolean)
		for item in search_result:
			hostid = item.host.hostid
			zi = Zabbixinterface.query.filter_by(hostid=hostid).first()
			if zi == None:
				continue
			if zi.ip == ip:
				result.append(item.itemid)

		return result

	@classmethod
	def find_hostid_for_table_row_instance(cls,row):
		ip = row[PER_INSTANCE_TABLE_HEAD.index(TABLE_HEAD_IP)]
		z_hostname = ip
		h = Zabbixhosts.query.filter_by(name=z_hostname).first()
		hostid = None
		if h != None:
			hostid = h.hostid
		return hostid

	@classmethod
	def find_item_list_for_table_row_aws_fee(cls,row):
		result = []
		metric_name = row[AWS_FEE_TABEL_HEAD.index(TABLE_HEAD_METRIC_NAME)]
		filter_boolean = ItemSearchValue2Filter.parse(metric_name)
		search_result = cls.search(filter_boolean)
		for item in search_result:
			if item.itemtype.aws != None:
				result.append(item.itemid)

		return result


	@classmethod
	def row_2_item_list(cls,row_type,row):
		type_func_map = {
			BY_GROUP_RESULT:cls.find_item_list_for_table_row_group,
			PER_INSTANCE_RESULT:cls.find_item_list_for_table_row_instance
		}

		for aws in Aws.query.all():
			type_func_map[aws.awsname] = cls.find_item_list_for_table_row_aws_fee

		result = []
		result = type_func_map.get(row_type)(row)
		return result


	@classmethod
	def row_type_2_name(cls,row_type,row):
		type_name_map = {
			BY_GROUP_RESULT : by_group_name,
			PER_INSTANCE_RESULT : per_instance_name
		}

		for aws in Aws.query.all():
			type_name_map[aws.awsname] = aws_fee_name

		return type_name_map.get(row_type,None)(row)

	@classmethod
	def hostid_2_availability(cls,hostid):
		available_status = None

		zh = Zabbixhosts.query.get(hostid)
		if zh != None:
			available_status = zh.available

		return available_status
	
	@classmethod
	def generate_per_instance_result_no_fee(cls,item_search_result,asg_name=None):
		result = {}
		table_head = PER_INSTANCE_TABLE_HEAD
		metric_count = 0
		metric_result = []

		for s in item_search_result:
			if s.itemtype.aws != None or s.itemtype.itemunit == None:
				continue

			if asg_name != None and s.host.service.servicename != asg_name:
				continue

			

			group_name = s.host.service.servicename

			instance_name = s.host.hostname

			ip = 'unkown'
			zi = Zabbixinterface.query.filter_by(hostid=s.host.hostid).first()
			if zi != None:
				ip = zi.ip

			metric_name = s.itemname

			available_status = cls.hostid_2_availability(s.host.hostid)

			row = [group_name,instance_name,ip,metric_name,available_status]
			assert len(row) == len(table_head)

			metric_result.append(row)

			metric_count += 1

		result['table_head'] = table_head
		result['metric_count'] = metric_count
		result['metric_result'] = metric_result

		return result

	@classmethod
	def generate_fee_data(cls,item_search_result,awsname):

		result = {}
		table_head = AWS_FEE_TABEL_HEAD
		metric_count = 0
		metric_result =[]

		for s in item_search_result:
			if s.itemtype.aws != None and s.itemtype.aws.awsname == awsname:
				metric_name = s.itemname
				row = [metric_name]

				assert len(row) == len(table_head)
				metric_result.append(row)
				metric_count += 1

		result['table_head'] = table_head
		result['metric_count'] = metric_count
		result['metric_result'] = metric_result

		return result

	@classmethod
	def item_list_2_unitname(cls,item_list):

		unit_name = 'unkown'

		for i in item_list:
			item = Item.query.get(i)
			if item == None:
				continue
			it = item.itemtype
			if it == None:
				continue

			unit_name = it.itemunit

		return unit_name

class ItemtypeSearchValue2Filter():

	@classmethod
	def parse(cls,search_value):
		filter_result = True
		if search_value == '' or search_value == None:
			filter_result = True
		else:
			filter_result = Itemtype.itemtypename.ilike('%' + search_value + '%')

		return filter_result

class ItemSearchValue2Filter():

	@classmethod
	def parse(cls,search_value):
		filter_result = None
		if search_value == '' or search_value == None:
			filter_result = True
		else:
			filter_result = Item.itemname.ilike('%' + search_value + '%')

		return filter_result



class SearchWithBasicMetrics(BaseSearch):
	
	@classmethod
	def search(cls,search_value=None,asg_name=None,desire_result_set=NO_FEE_RESULT_SET):

		result = {}

		filter_boolean = ItemSearchValue2Filter.parse(search_value)

		zi = Zbxitemtype.query.first()
		ni = Normalitemtype.query.first()
		zi_ni_it = zi.itemtypes.all() + ni.itemtypes.all()
		item_search_result = []


		for it in zi_ni_it:
			item_search_result += BaseSearch.search(it.items,filter_boolean)

		by_group_result = ItemSearch.generate_by_group_result_no_fee(item_search_result)
		per_instance_result = ItemSearch.generate_per_instance_result_no_fee(item_search_result)

		tablehead_result_map = {
			BY_GROUP_RESULT : by_group_result,
			PER_INSTANCE_RESULT : per_instance_result
		}

		for result_head in desire_result_set:
			result[result_head] = tablehead_result_map.get(result_head,None)

		# result[BY_GROUP_RESULT] = by_group_result
		# result[PER_INSTANCE_RESULT] = per_instance_result

		return result


class BrowseMetrics():

	@classmethod
	def browse(cls):
		result = {}

		for s in Service.query.all():
			result[s.servicename] = []
			for it in s.itemtypes.all():
				result[s.servicename].append(it.itemtypename)

		result['Basic Metrics'] = []

		zi = Zbxitemtype.query.first()
		ni = Normalitemtype.query.first()
		zi_ni_it = zi.itemtypes.all() + ni.itemtypes.all()

		for it in zi_ni_it:
			if it.aws != None or it.itemunit == None:
				continue
			result['Basic Metrics'].append(it.itemtypename)

		return result
		

class SearchInASGGroup():

	@classmethod
	def search(cls,search_value=None,asg_name=None,desire_result_set=NO_FEE_RESULT_SET):
		result = {}

		filter_boolean = ItemSearchValue2Filter.parse(search_value)

		asg_group = Service.query.filter_by(servicename=asg_name).first()
		
		if asg_group != None:
			item_search_result = []

			##### contains all basic metrics  ####
			for h in asg_group.hosts.all():
				item_search_result += BaseSearch.search(h.items,filter_boolean)

			# only for group-specific metrics
			# for it in asg_group.itemtypes.all():
			# 	item_search_result += BaseSearch.search(it.items,filter_boolean)			

			by_group_result = ItemSearch.generate_by_group_result_no_fee(item_search_result,asg_name)
			

			per_instance_result = ItemSearch.generate_per_instance_result_no_fee(item_search_result,asg_name)

			tablehead_result_map = {
				BY_GROUP_RESULT : by_group_result,
				PER_INSTANCE_RESULT : per_instance_result
			}

			for result_head in desire_result_set:
				result[result_head] = tablehead_result_map.get(result_head,None)

			# result[BY_GROUP_RESULT] = by_group_result
			# result[PER_INSTANCE_RESULT] = per_instance_result

		return result


class SearchWithAll():

	@classmethod
	def search(cls,search_value=None,asg_name=None,desire_result_set=NO_FEE_RESULT_SET):
		result = {}

		filter_boolean = ItemSearchValue2Filter.parse(search_value)

		item_search_result = ItemSearch.search(filter_boolean)

		by_group_result = ItemSearch.generate_by_group_result_no_fee(item_search_result)
		

		per_instance_result = ItemSearch.generate_per_instance_result_no_fee(item_search_result)

		tablehead_result_map = {
			BY_GROUP_RESULT : by_group_result,
			PER_INSTANCE_RESULT : per_instance_result
		}

		for result_head in desire_result_set:
			result[result_head] = tablehead_result_map.get(result_head,None)

		# result[BY_GROUP_RESULT] = by_group_result
		# result[PER_INSTANCE_RESULT] = per_instance_result

		return result

class SearchWithBilling():

	@classmethod
	def search(cls,search_value=None,option='',desire_result_set=None):
		result = {}

		filter_boolean = ItemSearchValue2Filter.parse(search_value)

		item_search_result = ItemSearch.search(filter_boolean)

		if desire_result_set == None:
			desire_result_set = []
			for aws in Aws.query.all():
				desire_result_set.append(aws.awsname)

		for aws in Aws.query.all():
			per_aws_fee_result = ItemSearch.generate_fee_data(item_search_result,aws.awsname)
			# print aws.awsname, desire_result_set
			if aws.awsname in desire_result_set:
				result[aws.awsname] = per_aws_fee_result

		# per_instance_result = ItemSearch.generate_fee_data(item_search_result)

		# result[] = per_instance_result
		return result


