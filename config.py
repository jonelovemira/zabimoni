import os
basedir = os.path.abspath(os.path.dirname(__file__))



SQLALCHEMY_DATABASE_URI = 'mysql://monitor:monitor@127.0.0.1/monitor2'
SQLALCHEMY_POOL_RECYCLE = 3600
ZBX_DATABASE_URL = 'mysql://zabbix:zabbix@127.0.0.1/zabbix'
    
# SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/testDatabase'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 1

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# administrator list
ADMINS = ['xuzhongyong@tp-link.net']



# area name of 
AREA = 'ap-southeast-1'
SERVICE = 'monitor'

# different path
GENERATE_REPORT_PATH = basedir + '/generate_report.py '
TMP_FILE = basedir + '/tmp/monitor.log'
REMOTE_COMMAND_LOG = basedir + '/remote_command'
AGENT_CONFIG_FILE = '/etc/zabbix/zabbix_agentd.conf'
GENERATE_REPORT_ROUTE = '/chart/report/generate'
PHANTOMJS = basedir + '/monitor/static/js/export/generate/phantomjs'
HIGHCHART_CONVERT = basedir + '/monitor/static/js/export/highcharts-convert.js'
REPORT_OUTPUT_DIR = basedir + '/monitor/static/report/'
REPORT_OUTPUT_WIDTH = '2400'
REPORT_OUTPUT_TYPE = 'StockChart'
REPORT_OUTPUT_SCALE = '1'
S3_BUCKET_NAME = 'ipcamera-statics-us'
S3_BUCKET_FOLDER = 'monitor-server/report/'
S3_SCHEDULE_FOLDER = 'monitor-server/schedule/'
SCHEDULE_ALL_FILENAME = 'all'
XML_EXPORT_PATH = 'monitor-server/monitor.xml'

AUTOSCALE_COMMAND_PATH = basedir + '/autoscale_group.py'
EMAIL_NOTIFICATION_COMMAND_PATH = basedir + '/sendemail'

# chart init timelength in seconds
CHART_INIT_TIME = 86400

# chart history timelength in seconds
CHART_HISTORY_TIME = 2592000

DESIRED_DISPLAY_POINTS = 150
RESOLUTION = 60
SECOND_TO_MILLI = 1000

AUTOSCALE = 2
EMAILNOTIFICATION = 1


# bind to read only zabbix database
SQLALCHEMY_BINDS = {
	'zabbix': 'mysql://zabbix:zabbix@127.0.0.1/zabbix'
}


