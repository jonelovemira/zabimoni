#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import csv, inspect, os, sys, traceback

currentdir = os.path.dirname(os.path.abspath(\
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

from monitor.billing.models import *
from monitor import db

for apio in apioperation.query.all():
    db.session.delete(apio)

for lc in linkedaccount.query.all():
    db.session.delete(lc)

for p in payeraccount.query.all():
    db.session.delete(p)

for s in awsservice.query.all():
    db.session.delete(s)

for az in availablezone.query.all():
    db.session.delete(az)

for br in billingrow.query.all():
    db.session.delete(br)

for i in invoice.query.all():
    db.session.delete(i)

db.session.commit()