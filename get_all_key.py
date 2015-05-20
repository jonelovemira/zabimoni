#! flask/bin/python

from monitor.item.models import Service,Zbxitemtype,Normalitemtype,Itemtype

output = file('itemtype.txt','wb')

dot_num = 100
line_num = 100

for s in Service.query.all():
	output.write('\n' + '*'*dot_num + '\n')
	output.write(s.servicename + ' : \n')
	for it in s.itemtypes.all():
		tmp_str = '\t%s\t\t\t\t\t%s\t%s\n' % ( it.itemtypename,it.zabbixvaluetype, it.itemunit)
		output.write('-'*line_num + '\n')
		output.write(tmp_str)
	output.write('*'*dot_num + '\n')


output.write('\n\n' + '*'*dot_num + '\n')
output.write('zabbix auto monitoring healthy data : \n')
for it in Zbxitemtype.query.first().itemtypes.all():
	tmp_str = '\t%s\t%s\t%s\n' % ( it.itemtypename,it.zabbixvaluetype, it.itemunit)
	output.write('-'*line_num + '\n')
	output.write(tmp_str)
output.write('*'*dot_num + '\n')

output.write('\n\n' + '*'*dot_num + '\n')
output.write('all : \n')
for it in Normalitemtype.query.first().itemtypes.all():
	tmp_str = '\t%s\t%s\t%s\n' % ( it.itemtypename,it.zabbixvaluetype, it.itemunit)
	output.write('-'*line_num + '\n')
	output.write(tmp_str)
output.write('*'*dot_num + '\n')

output.write('\n\n' + '*'*dot_num + '\n')
output.write('aws fee items :\n')
for it in Itemtype.query.all():
	if it.aws != None:
		tmp_str = '\t%s\t%s\t%s\n' % ( it.itemtypename,it.zabbixvaluetype, it.itemunit)
		output.write('-'*line_num + '\n')
		output.write(tmp_str)
output.write('*'*dot_num + '\n')

output.close()