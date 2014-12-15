#! /home/jone/flask_project/monitor-0.3.7/flask/bin/python

import sys
from datetime import datetime


if __name__ == '__main__':
	#test if can execute
	content = 'new content'
	if len(sys.argv) > 1:
		content = 	sys.argv[1]
	today = datetime.today()
	output = open('/home/jone/flask_project/monitor-0.3.7/remote_command','a')
	output.write('\n')
	output.write(str(today))
	output.write(' ' + content)
	output.close()


