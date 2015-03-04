#! /home/monitor/project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Trigger,Area
import boto.ec2.autoscale
import sys,time
from config import REMOTE_COMMAND_LOG,ASG_SCALE_UP,ASG_SCALE_DOWN,AREA

if __name__ == '__main__':

	time_format = '%Y-%m-%d %H:%M:%S %Z'
	current_time = time.strftime(time_format,time.gmtime(time.time()))

	output = open(REMOTE_COMMAND_LOG,'a')
	output.write( '\n' + current_time + ' ')

	for a in sys.argv:
		output.write(a + ' ')

	output.close()

	if len(sys.argv) < 2:
		return

	asggroupname = sys.argv[1]
	asgscaletype = sys.argv[2]

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
	print new_desired_capacity



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




