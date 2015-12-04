from config import BY_GROUP_TABLE_HEAD, PER_INSTANCE_TABLE_HEAD,\
                    AWS_FEE_TABEL_HEAD, BY_GROUP_RESULT, PER_INSTANCE_RESULT,\
                    TABLE_HEAD_GROUP_NAME, TABLE_HEAD_METRIC_NAME, \
                    TABLE_HEAD_ALIAS, TABLE_HEAD_DESCRIPTION, \
                    TABLE_HEAD_INSTANCE_NAME, TABLE_HEAD_IP, \
                    TABLE_HEAD_AVAILABILITY

from monitor.item.models import Aws, Itemtype, Item

from monitor.functions import function_input_checker


class RowContentGeneratorFactory():
    """docstring for ContentGeneratorFactory"""
    def __init__(self):
        pass

    @function_input_checker(None)
    def produce_generator(self, rowtype):

        grouptype_generator_map = {
            BY_GROUP_RESULT: ByGroupRowContentGenerator(),
            PER_INSTANCE_RESULT: PerInstanceRowContentGenerator()
        }

        for aws in Aws.query.all():
            grouptype_generator_map[aws.awsname] = AwsFeeRowContentGenerator()

        result = grouptype_generator_map.get(rowtype, None)

        assert result is not None, 'some of your table type: %s is ' + \
            'not registed in the RowContentGeneratorFactory' % (rowtype)

        return result

class RowContentGenerator():
    """docstring for RowContentGenerator"""
    def __init__(self):
        self.defaults = {}

    @function_input_checker(None)
    def id_2_content(self, item, head):

        arr = []

        for tdtype in head:
            if item.host != None and item.host.hostid != None and \
                self.defaults.has_key(item.host.hostid) and \
                self.defaults[item.host.hostid] != None and \
                self.defaults[item.host.hostid].has_key(tdtype):
                td_result = self.defaults[item.host.hostid][tdtype]
            else:
                td_generator = TdContentGeneratorFactory().\
                    produce_generator(tdtype)
                td_result = td_generator.id_2_content(item)
                if td_generator.can_be_default:
                    if not self.defaults.has_key(item.host.hostid):
                        self.defaults[item.host.hostid] = {}
                    self.defaults[item.host.hostid][tdtype] = td_result
            arr.append(td_result)

        assert len(arr) == len(head)

        return arr

    @function_input_checker(None)
    def get_series_name(self, content):
        assert len(content) == len(self.get_head()), 'unmatch length'

        item_list = self.content_2_id(content)

        if TABLE_HEAD_ALIAS in self.get_head() >= 0:
            result = content[self.get_head().index(TABLE_HEAD_ALIAS)]
        else:
            result = content[self.get_head().index(TABLE_HEAD_METRIC_NAME)]

        if result == TABLE_HEAD_ALIAS:
            result = content[self.get_head().index(TABLE_HEAD_METRIC_NAME)]

        if len(item_list) > 0:
            item = Item.query.get(item_list[0])
            if item is not None and item.itemtype is not None and \
                item.itemtype.itemtypename is not None:
                result = item.itemtype.itemtypename

        return result

        

class ByGroupRowContentGenerator(RowContentGenerator):
    """docstring for ByGroupRowContentGenerator"""
    def __init__(self):
        RowContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        head = self.get_head()

        return RowContentGenerator.id_2_content(self, item, head)

    @function_input_checker(None)
    def get_head(self):

        head = BY_GROUP_TABLE_HEAD

        return head

    @function_input_checker(None)
    def content_2_id(self, content):

        assert len(content) == len(self.get_head()), 'unmatch length'

        metric_name = content[self.get_head().index(TABLE_HEAD_METRIC_NAME)]
        service_name = content[self.get_head().index(TABLE_HEAD_GROUP_NAME)]
        
        its = Itemtype.query.filter_by(itemkey=metric_name).all()

        item_list = []

        for it in its:
            for i in it.items.all():
                if i is not None and i.host is not None and i.host.service is \
                    not None and i.host.service.servicename == service_name:
                    item_list.append(i.itemid)

        return item_list

    @function_input_checker(None)
    def get_series_name(self, content):
        assert len(content) == len(self.get_head()), 'unmatch length'

        item_list = self.content_2_id(content)

        metric_result = content[self.get_head().index(TABLE_HEAD_METRIC_NAME)]

        if len(item_list) > 0:
            item = Item.query.get(item_list[0])
            if item is not None and item.itemtype is not None and \
                item.itemtype.itemtypename is not None:
                metric_result = item.itemtype.itemtypename

        result = content[self.get_head().index(TABLE_HEAD_GROUP_NAME)] + ' ' +\
            metric_result

        return result

    @function_input_checker(None)
    def get_fake_row(self, groupname, metric_name):
        
        tmp_row = list(self.get_head())
        tmp_row[self.get_head().index(TABLE_HEAD_GROUP_NAME)] = groupname
        tmp_row[self.get_head().index(TABLE_HEAD_METRIC_NAME)] = metric_name

        return tmp_row


class PerInstanceRowContentGenerator(RowContentGenerator):
    """docstring for PerInstanceRowContentGenerator"""
    def __init__(self):
        RowContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):

        head = self.get_head()
        content = RowContentGenerator.id_2_content(self, item, head)

        return content

    @function_input_checker(None)
    def get_head(self):

        head = PER_INSTANCE_TABLE_HEAD

        return head

    @function_input_checker(None)
    def content_2_id(self, content):

        assert len(content) == len(self.get_head()), 'unmatch length'

        result = []
        metric_name = content[self.get_head().\
            index(TABLE_HEAD_METRIC_NAME)]
        ip = content[self.get_head().index(TABLE_HEAD_IP)]

        its = Itemtype.query.filter_by(itemkey=metric_name).all()

        item_list = []

        for it in its:
            for i in it.items.all():
                if i is not None and i.get_host_ip() == ip:
                    item_list.append(i.itemid)

        return item_list

    @function_input_checker(None)
    def get_hostids(self, content):

        assert len(content) == len(self.get_head()), 'unmatch length'

        item_list = self.content_2_id(content)

        hostids = []
        for iid in item_list:
            item = Item.query.get(iid)
            if item is not None and item.host is not None and item.host.hostid\
                 is not None:
                hostids.append(item.host.hostid)

        return hostids

    @function_input_checker(None)
    def get_series_name(self, content):
        assert len(content) == len(self.get_head()), 'unmatch length'

        item_list = self.content_2_id(content)

        metric_result = content[self.get_head().index(TABLE_HEAD_METRIC_NAME)]

        if len(item_list) > 0:
            item = Item.query.get(item_list[0])
            if item is not None and item.itemtype is not None and \
                item.itemtype.itemtypename is not None:
                metric_result = item.itemtype.itemtypename

        result = content[self.get_head().index(TABLE_HEAD_IP)] + ' ' +\
            metric_result

        return result

    @function_input_checker(None)
    def get_fake_row(self, ip, metric_name):
        
        tmp_row = list(self.get_head())
        tmp_row[self.get_head().index(TABLE_HEAD_IP)] = ip
        tmp_row[self.get_head().index(TABLE_HEAD_METRIC_NAME)] = metric_name

        return tmp_row

        

class AwsFeeRowContentGenerator(RowContentGenerator):
    """docstring for AwsFeeRowContentGenerator"""
    def __init__(self):
        RowContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        head = self.get_head()

        return RowContentGenerator.id_2_content(self, item, head)

    @function_input_checker(None)
    def get_head(self):

        head = AWS_FEE_TABEL_HEAD

        return head

    @function_input_checker(None)
    def content_2_id(self, content):

        assert len(content) == len(self.get_head()), 'unmatch length'

        metric_name = content[self.get_head().\
            index(TABLE_HEAD_METRIC_NAME)]

        its = Itemtype.query.filter_by(itemkey=metric_name).all()

        item_list = []

        for it in its:
            if it.aws != None:
                for i in it.items.all():
                    if i.itemid != None:
                        item_list.append(i.itemid)

        return item_list

    @function_input_checker(None)
    def get_fake_row(self, metric_name):
        
        tmp_row = list(self.get_head())
        tmp_row[self.get_head().index(TABLE_HEAD_METRIC_NAME)] = metric_name

        return tmp_row
        

class TdContentGeneratorFactory():
    """docstring for TdContentGeneratorFactory"""
    def __init__(self):
        pass

    @function_input_checker(None)
    def produce_generator(self, tdtype):
        
        tdtype_generator_map = {
            TABLE_HEAD_GROUP_NAME: GroupNameTdGenerator(), 
            TABLE_HEAD_METRIC_NAME: MetricNameTdGenerator(),
            TABLE_HEAD_ALIAS: AlaisTdGenerator(), 
            TABLE_HEAD_DESCRIPTION: DescriptionTdGenerator(), 
            TABLE_HEAD_INSTANCE_NAME: InstanceNameTdGenerator(), 
            TABLE_HEAD_IP: IpTdGenerator(), 
            TABLE_HEAD_AVAILABILITY: AvailablityTdGenerator()
        }

        result = tdtype_generator_map.get(tdtype, None)

        assert result is not None, 'some of your td head: %s is ' + \
            'not registed in the TdContentGeneratorFactory' % (rowtype)

        return result

class TdContentGenerator():
    """docstring for TdContentGenerator"""
    def __init__(self):
        self.can_be_default = False
        



class GroupNameTdGenerator(TdContentGenerator):
    """docstring for GroupNameTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        assert item.host is not None, 'item input: %s in '\
            'GroupNameTdGenerator does not belong to any host.' % (item)

        assert item.host.service is not None, 'Host holding self item %s in' + \
            'GroupNameTdGenerator does not belong to any service.' % (item)

        result = item.host.service.servicename

        assert result is not None, 'GroupNameTdGenerator returns empty'

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass

class MetricNameTdGenerator(TdContentGenerator):
    """docstring for MetricNameTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        assert item.itemtype is not None, 'item input: in '\
            'MetricNameTdGenerator does not belong to any itemtype.' % (item)

        result = item.itemtype.itemkey

        assert result is not None, 'MetricNameTdGenerator returns empty'

        return result


    @function_input_checker(None)
    def content_2_id(self, content):
        pass

class AlaisTdGenerator(TdContentGenerator):
    """docstring for AlaisTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        assert item.itemtype is not None, 'item input: in '\
            'AlaisTdGenerator does not belong to any itemtype.' % (item)

        result = item.itemtype.itemtypename

        assert result is not None, 'AlaisTdGenerator returns empty'

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass
        
class DescriptionTdGenerator(TdContentGenerator):
    """docstring for DescriptionTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):
        
        assert item.itemtype is not None, 'item input: in '\
            'DescriptionTdGenerator does not belong to any itemtype.' % (item)

        result = item.itemtype.description or ""

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass
        
class InstanceNameTdGenerator(TdContentGenerator):
    """docstring for InstanceNameTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        pass

    @function_input_checker(None)
    def id_2_content(self, item):

        assert item.host is not None, 'item input: in '\
            'InstanceNameTdGenerator does not belong to any host.' % (item)

        result = item.host.hostname

        assert result is not None, 'InstanceNameTdGenerator returns empty'

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass
        
class IpTdGenerator(TdContentGenerator):
    """docstring for IpTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        self.can_be_default = True

    @function_input_checker(None)
    def id_2_content(self, item):
        
        result = item.get_host_ip()

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass
        
class AvailablityTdGenerator(TdContentGenerator):
    """docstring for AvailablityTdGenerator"""
    def __init__(self):
        TdContentGenerator.__init__(self)
        self.can_be_default = True

    @function_input_checker(None)
    def id_2_content(self, item):
        
        result = item.get_available_status()

        return result

    @function_input_checker(None)
    def content_2_id(self, content):
        pass
             
        
        
        
        
        
        
    

