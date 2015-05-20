#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config


from monitor import db


import sys
from datetime import datetime
# from ..monitor import db

if __name__ == '__main__':
	#test if can execute
	content = 'new content'
	if len(sys.argv) > 1:
		content = 	sys.argv[1]
	today = datetime.today()
	output = open('/home/monitor/project/monitor-0.3.7/remote_command','a')
	output.write('\n')
	output.write(str(today))
	output.write(' ' + content)
	output.close()


