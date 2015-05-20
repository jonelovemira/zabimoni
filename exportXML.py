#! flask/bin/python

from boto.s3.connection import S3Connection
from config import S3_BUCKET_NAME,XML_EXPORT_PATH
from monitor.item.models import Service,Itemtype
from tempfile import NamedTemporaryFile
import sys,os

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

def export_all_2_xml():
	root = ET.Element('monitor')
	services = Service.query.all()
	for s in services:
		s_tmp_e = ET.Element('service')
		s_tmp_e.set('servicename',s.servicename)
		root.append(s_tmp_e)

	its = Itemtype.query.all()
	for it in its:
		if it.aws != None:
			continue
		i_tmp_e = ET.Element('itemtype')
		i_tmp_e.set('itemtypename',it.itemtypename)
		i_tmp_e.set('itemkey',it.itemkey)
		i_tmp_e.set('itemdatatypename',it.itemdatatype.itemdatatypename)
		if it.itemunit != None:
			i_tmp_e.set('itemunit',it.itemunit)
		if it.zabbixvaluetype != None:
			i_tmp_e.set('zabbixvaluetype',str(it.zabbixvaluetype))
		i_tmp_e.set('time_frequency',str(it.time_frequency))
		i_tmp_e.set('function_type',str(it.function_type))

		it_services = it.service.all()
		for it_s in it_services:
			i_s_tmp_e = ET.Element('itservice')
			i_s_tmp_e.set('servicename',it_s.servicename)
			i_tmp_e.append(i_s_tmp_e)
		root.append(i_tmp_e)

	# print root
	tree = ET.ElementTree(root)
	f = NamedTemporaryFile(delete=False)
	tree.write(f.name)
	f.close()

	#con = S3Connection()
	#bucket = con.get_bucket(S3_BUCKET_NAME)
	#key = bucket.get_key(XML_EXPORT_PATH)
	#if key == None:
	#	key = bucket.new_key(XML_EXPORT_PATH)

	#key.set_contents_from_filename(f.name)
	#key.make_public()
	#os.unlink(f.name)

	

if __name__ == '__main__':
	export_all_2_xml()
