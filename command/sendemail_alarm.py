#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

import boto.sns
import sys,time
from config import AREA,REMOTE_COMMAND_LOG
from monitor.functions import log_for_callback_command

import getopt

def send_sns_mail(topic_arn,hostinfo,metric_name,alarm_value,current_value):
	try:
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
		raise e

def usage():
	print("Usage:%s [-t|-i|-m|-a|-c] [--help|--topicarn|--hostinfo|--metricname|--alarmvalue|--currentvalue] args ...." % sys.argv[0])

if __name__ == '__main__':

	log_for_callback_command(sys.argv)

	# get args
	try:
		opts,args = getopt.getopt(sys.argv[1:], "ht:i:m:a:c:", ["help","topicarn=","hostinfo=","metricname=","alarmvalue=","currentvalue="])
		for opt,arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit(1)
			elif opt in ("-t","--topicarn"):
				topicarn = arg
			elif opt in ("-i", "--hostinfo"):
				hostinfo = arg
			elif opt in ("-m","--metricname"):
				metricname = arg
			elif opt in ("-a","--alarmvalue"):
				alarmvalue = arg
			elif opt in ("-c","--currentvalue"):
				currentvalue = arg
			else:
				usage()
				sys.exit(1)
		for arg in args:
			print "non-option ARGV-elements: %s" % arg
	except getopt.GetoptError, exc:
		print "%s" % exc.msg
		usage()
		sys.exit(1)

	# print topicarn,hostinfo,metricname,alarmvalue,currentvalue
	send_sns_mail(topicarn,hostinfo,metricname,alarmvalue,currentvalue)
	# try:
	# 	topic_arn = sys.argv[1]
	# 	# messages = sys.argv[2]
	# 	hostinfo = sys.argv[2]

	# 	metric_name = sys.argv[3]

	# 	alarm_value = sys.argv[4]
	# 	current_value = sys.argv[5]

		

	# 	messages = ''
	# 	messages += 'Time : ' + current_time + '\n'
	# 	messages += 'Host info : ' + hostinfo + '\n'
	# 	messages += 'Metric Name : ' + metric_name + '\n'
	# 	messages += 'Alarm setting Value : ' + alarm_value + '\n'
	# 	messages += 'Metric Current Value : ' + current_value + '\n'


	# 	# print messages

	# 	con = boto.sns.connect_to_region(AREA)

	# 	con.publish(topic = topic_arn,message = messages, subject = 'Monitor alarms')
	# except Exception, e:
	# 	topic_arn = sys.argv[1]
	# 	messages = sys.argv[2]

	# 	con = boto.sns.connect_to_region(AREA)

	# 	con.publish(topic = topic_arn,message = messages, subject = 'Monitor alarms')

	