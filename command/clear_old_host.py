#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config


from monitor.functions import log_for_callback_command
from monitor.zabbix.models import loadSession, Zabbixinterface
from monitor import db
from monitor.item.models import Host

import getopt, sys

def clear_host(instanceip):
    if instanceip is None:
        raise Exception('instanceip is None')

    session = loadSession()
    i = session.query(Zabbixinterface).filter_by(ip=instanceip).first()
    session.close()

    if i == None:
        raise Exception('interface for this ip do not exist')

    hostid = i.hostid

    host = Host.query.filter_by(hostid=hostid).first()
    if host != None:
        for i in host.items.all():
            db.session.delete(i)
        
        db.session.delete(host)

    db.session.commit()


def usage():
    print("Usage:%s [-i|-h] [--help|--instanceip] args ...." % sys.argv[0])

if __name__ == '__main__':


    log_for_callback_command(sys.argv)
    
    instanceip = None

    try:
        opts,args = getopt.getopt(sys.argv[1:], "i:", ["help","instanceip="])
        for opt,arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit(1)
            elif opt in ("-i", "--instanceip"):
                instanceip = arg
            else:
                usage()
                sys.exit(1)
        for arg in args:
            print "non-option ARGV-elements: %s" % arg
    except getopt.GetoptError, exc:
        print "%s" % exc.msg
        usage()
        sys.exit(1)

    clear_host(instanceip)