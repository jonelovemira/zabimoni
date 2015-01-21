#! /home/monitor/project/monitor-0.3.7/flask/bin/python
import boto.sns
import sys
from config import AREA

if __name__ == '__main__':
	topic_arn = sys.argv[1]
	messages = sys.argv[2]

	con = boto.sns.connect_to_region(AREA)

	con.publish(topic = topic_arn,message = messages, subject = 'Monitor alarms')