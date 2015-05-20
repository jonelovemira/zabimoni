#! flask/bin/python

from monitor.zabbix.zabbix_api import zabbix_api
from monitor.zabbix.models import loadSession
from monitor.zabbix.models import Zabbixhosts
from config import TEMPLATE_GROUP_SPLITER

z = zabbix_api()
session = loadSession()
services_template = session.query(Zabbixhosts).filter(Zabbixhosts.name.ilike('%' + TEMPLATE_GROUP_SPLITER + '%')).all()
tids = []
for st in services_template:
    tids.append(st.hostid)

session.close()
z.template_delete_without_clear(tids)
z.template_delete(tids)