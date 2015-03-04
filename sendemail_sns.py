#! /home/monitor/project/monitor-0.3.7/flask/bin/python
import boto.sns
import sys,time
from config import AREA,REMOTE_COMMAND_LOG

if __name__ == '__main__':

	time_format = '%Y-%m-%d %H:%M:%S %Z'
	current_time = time.strftime(time_format,time.gmtime(time.time()))

	output = open(REMOTE_COMMAND_LOG,'a')
	output.write( '\n' + current_time + ' ')

	for a in sys.argv:
		output.write(a + ' ')

	output.close()

	try:
		topic_arn = sys.argv[1]
		# messages = sys.argv[2]
		hostinfo = sys.argv[2]

		metric_name = sys.argv[3]

		alarm_value = sys.argv[4]
		current_value = sys.argv[5]

		

		messages = ''
		messages += 'Time : ' + current_time + '\n'
		messages += 'Host info : ' + hostinfo + '\n'
		messages += 'Metric Name : ' + metric_name + '\n'
		messages += 'Alarm setting Value : ' + alarm_value + '\n'
		messages += 'Metric Current Value : ' + current_value + '\n'


		# print messages

		con = boto.sns.connect_to_region(AREA)

		con.publish(topic = topic_arn,message = messages, subject = 'Monitor alarms')
	except Exception, e:
		topic_arn = sys.argv[1]
		messages = sys.argv[2]

		con = boto.sns.connect_to_region(AREA)

		con.publish(topic = topic_arn,message = messages, subject = 'Monitor alarms')

	