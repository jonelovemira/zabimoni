#! /home/monitor/project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Trigger,Area
import boto.ec2.autoscale
import sys

if __name__ == '__main__':
	triggername = sys.argv[1]
	t = Trigger.query.filter_by(triggername=triggername).first()
	actions = t.actions.all()

	for a in actions:
		if a.autoscalegroupname == None:
			continue
		autoscalegroupname = a.autoscalegroupname
		autoscaletype = a.autoscaletype
		areaid = a.areaid

		areaname = Area.query.filter_by(areaid=areaid).first().areaname
		con = boto.ec2.autoscale.connect_to_region(areaname)
		autoscalegroup = con.get_all_groups(names=[autoscalegroupname])[0]
		desired_capacity = autoscalegroup.desired_capacity
		max_size = autoscalegroup.max_size
		min_size = autoscalegroup.min_size
		future_dc = desired_capacity
		if autoscaletype == 0:
			future_dc += 1
		else:
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




