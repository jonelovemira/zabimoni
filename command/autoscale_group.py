#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

from monitor.functions import log_for_callback_command

from monitor.item.models import Trigger,Area
import boto.ec2.autoscale
import sys,time
from config import REMOTE_COMMAND_LOG,ASG_SCALE_UP,ASG_SCALE_DOWN,AREA
import getopt

def scale(asggroupname,asgscaletype):
	con = boto.ec2.autoscale.connect_to_region(AREA)
	autoscalegroup = con.get_all_groups(names=[asggroupname])[0]
	desired_capacity = autoscalegroup.desired_capacity
	max_size = autoscalegroup.max_size
	min_size = autoscalegroup.min_size
	future_dc = desired_capacity
	if asgscaletype == ASG_SCALE_UP:
		future_dc += 1
	elif asgscaletype == ASG_SCALE_DOWN:
		future_dc -= 1

	if future_dc < min_size :
		future_dc = min_size
	if future_dc > max_size:
		future_dc = max_size

	autoscalegroup.set_capacity(future_dc)

	# verfy autoscaled
	newautoscalegroup = con.get_all_groups(names=[autoscalegroupname])[0]
	new_desired_capacity = newautoscalegroup.desired_capacity
	# print new_desired_capacity

def usage():
	print("Usage:%s [-g|-t|-h] [--help|--asggroupname|--asgscaletype] args ...." % sys.argv[0])

if __name__ == '__main__':

	log_for_callback_command(sys.argv)

	try:
		opts,args = getopt.getopt(sys.argv[1:], "g:t:", ["help","asggroupname=","asgscaletype="])
		for opt,arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit(1)
			elif opt in ("-g", "--asggroupname"):
				asggroupname = arg
			elif opt in ("-t","--asgscaletype"):
				asgscaletype = arg
			else:
				usage()
				sys.exit(1)
		for arg in args:
			print "non-option ARGV-elements: %s" % arg
	except getopt.GetoptError, exc:
		print "%s" % exc.msg
		usage()
		sys.exit(1)

	print asggroupname,asgscaletype
	# scale(asggroupname,asgscaletype)
	

	



	# triggername = sys.argv[1]
	# t = Trigger.query.filter_by(triggername=triggername).first()
	# actions = t.actions.all()

	# for a in actions:
	# 	if a.autoscalegroupname == None:
	# 		continue
	# 	autoscalegroupname = a.autoscalegroupname
	# 	autoscaletype = a.autoscaletype
	# 	areaid = a.areaid

	# 	areaname = Area.query.filter_by(areaid=areaid).first().areaname
	# 	con = boto.ec2.autoscale.connect_to_region(areaname)
	# 	autoscalegroup = con.get_all_groups(names=[autoscalegroupname])[0]
	# 	desired_capacity = autoscalegroup.desired_capacity
	# 	max_size = autoscalegroup.max_size
	# 	min_size = autoscalegroup.min_size
	# 	future_dc = desired_capacity
	# 	if autoscaletype == 0:
	# 		future_dc += 1
	# 	else:
	# 		future_dc -= 1

	# 	if future_dc < min_size :
	# 		future_dc = min_size

	# 	if future_dc > max_size:
	# 		future_dc = max_size

	# 	autoscalegroup.set_capacity(future_dc)

	# 	# verfy autoscaled
	# 	newautoscalegroup = con.get_all_groups(names=[autoscalegroupname])[0]
	# 	new_desired_capacity = newautoscalegroup.desired_capacity
	# 	print new_desired_capacity




