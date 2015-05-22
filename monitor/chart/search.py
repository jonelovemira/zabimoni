from monitor.chart.indextable import RowContentGeneratorFactory
from monitor.item.models import Item, Itemtype, Service, Aws, Zbxitemtype, \
						Normalitemtype
from config import BY_GROUP_RESULT, PER_INSTANCE_RESULT, NO_FEE_RESULT_SET
from monitor.functions import function_input_checker


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
	def it_search(cls, filter_boolean):
		result = BaseSearch.search(Itemtype.query, filter_boolean)
		return result

	@classmethod
	def generate_by_group_result_no_fee(cls,item_search_result,asg_name=None):
		result = {}
		
		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(BY_GROUP_RESULT)

		assert row_content_generator != None, 'Row type do not exists'

		table_head = row_content_generator.get_head()
		metric_count = 0
		metric_result = []
		for s in item_search_result:
			if s.itemtype.aws != None or s.itemtype.itemunit == None :
				continue

			if s.itemtype.zabbixvaluetype is not None and int(s.itemtype.zabbixvaluetype) not in [0, 3, 15]:
				continue

			if asg_name != None and s.host.service.servicename != asg_name:
				continue

			if s.host.service is None:
				continue

			try:
				tmp_row = row_content_generator.id_2_content(s)
			except Exception, e:
				continue


			if tmp_row not in metric_result:
				metric_result.append(tmp_row)
				metric_count += 1

		result['table_head'] = table_head
		result['metric_count'] = metric_count
		result['metric_result'] = metric_result
		return result

	@classmethod
	def find_item_list_for_table_row_group(cls,row):

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(BY_GROUP_RESULT)

		assert row_content_generator != None, 'Row type do not exists'

		result = row_content_generator.content_2_id(row)

		return result

	@classmethod
	def find_item_list_for_table_row_instance(cls,row):

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(PER_INSTANCE_RESULT)

		assert row_content_generator != None, 'Row type do not exists'

		result = row_content_generator.content_2_id(row)

		return result


	@classmethod
	def find_hostid_for_table_row_instance(cls,row):

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(PER_INSTANCE_RESULT)

		assert row_content_generator != None, 'Row type do not exists'

		hostids = row_content_generator.get_hostids(row)

		return hostids[0] if len(hostids) > 0 else None


	@classmethod
	def find_item_list_for_table_row_aws_fee(cls,row):

		tmp_aws = Aws.query.first()

		assert tmp_aws != None, 'no aws in database currently'
		assert tmp_aws.awsname != None, 'fee name can not be empty'

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(tmp_aws.awsname)

		assert row_content_generator != None, 'Row type do not exists'

		result = row_content_generator.content_2_id(row)

		return result


	@classmethod
	def row_2_item_list(cls,row_type,row):

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(row_type)

		assert row_content_generator != None, 'Row type do not exists'

		result = row_content_generator.content_2_id(row)

		return result

	@classmethod
	def row_type_2_name(cls,row_type,row):

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(row_type)

		assert row_content_generator != None, 'Row type do not exists'

		result = row_content_generator.get_series_name(row)

		return result




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

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(PER_INSTANCE_RESULT)

		assert row_content_generator != None, 'Row type do not exists'

		metric_count = 0
		metric_result = []
		table_head = row_content_generator.get_head()

		for s in item_search_result:
			if s.itemtype.aws != None or s.itemtype.itemunit == None :
				continue

			if s.itemtype.zabbixvaluetype is not None and int(s.itemtype.zabbixvaluetype) not in [0, 3, 15]:
				continue

			if asg_name != None and s.host.service.servicename != asg_name:
				continue

			try:
				row = row_content_generator.id_2_content(s)
			except Exception, e:
				continue

			metric_result.append(row)

			metric_count += 1

		result['table_head'] = table_head
		result['metric_count'] = metric_count
		result['metric_result'] = metric_result

		return result

	@classmethod
	def generate_fee_data(cls,item_search_result,awsname):

		result = {}
		# table_head = AWS_FEE_TABEL_HEAD

		row_content_generator = RowContentGeneratorFactory()\
			.produce_generator(awsname)

		assert row_content_generator != None, 'Row type do not exists'

		table_head = row_content_generator.get_head()

		metric_count = 0
		metric_result =[]

		for s in item_search_result:
			if s.itemtype.aws != None and s.itemtype.aws.awsname == awsname:
				
				try:
					row = row_content_generator.id_2_content(s)
				except Exception, e:
					continue

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
			filter_result = Itemtype.itemkey.ilike(search_value)

		return filter_result

class ItemSearchValue2Filter():

	@classmethod
	def parse(cls,search_value):
		filter_result = None
		if search_value == '' or search_value == None:
			filter_result = True
		else:
			filter_result = Item.itemname.ilike(search_value)

		return filter_result



class SearchWithBasicMetrics(BaseSearch):
	
	@classmethod
	def search(cls,search_value=None,asg_name=None,desire_result_set=NO_FEE_RESULT_SET):

		search_value = None
		desire_result_set=NO_FEE_RESULT_SET

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

		search_value = None
		desire_result_set=NO_FEE_RESULT_SET

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

		search_value = None
		desire_result_set=NO_FEE_RESULT_SET

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

		search_value = None
		desire_result_set = None

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


