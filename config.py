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
AREA = 'ap-northeast-1'
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

S3_MONITOR_BUCKET_NAME = 'ipcamera-monitor-alpha'
S3_MONITOR_REPORT_FOLDER = AREA + '/' + 'report/'
S3_MONITOR_SCHEDULE_FOLDER = AREA + '/' + 'schedule/'
S3_MONITOR_SHEDULE_ALL_FILENAME = 'all'

LOCAL_XML_EXPORT_PATH = basedir + '/monitor.xml'

AUTOSCALE_COMMAND_PATH = basedir + '/autoscale_group.py'

EMAIL_SNS_PATH = basedir + '/sendemail_sns.py'

EMAIL_NORMAL_PATH = basedir + '/sendemail_normal'

# chart init timelength in seconds
CHART_INIT_TIME = 3600

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

# host group name
HOST_GROUP_NAME = 'AWS servers'

# template name
TEMPLATE_NAME = 'Template OS Linux'

# zabbix value type
NUMERIC_FLOAT = 0
CHARACTER = 1
LOG = 2
NUMERIC_UNSIGNED = 3
TEXT = 4

# current server ip
CURRENT_SERVER_IP = '192.168.221.130'

# generate report script path
GENERATE_REPORT_SCRIPT_PATH = '/home/jone/flask_project/monitor-0.3.6/'

# kinds of adding itemtype
BY_ALL = 1
BY_AREA = 2
BY_SERVICE = 3
BY_HOST = 4

# Authorization Server
AUTHORIZATION_SERVER = 'jp.ops-beta.tplinkcloud.com'
AUTHORIZATION_VIEW = '/auth'
AUTHORIZATION_PROTOCAL = 'https://'

# Deploy in local or not
IN_LOCAL = True

# use SNS or not
MAIL_USE_SNS = True


# search config
BY_GROUP_RESULT = 'by_group_result'
PER_INSTANCE_RESULT = 'per_instance_result'
TABLE_HEAD_GROUP_NAME = 'Group Name'
TABLE_HEAD_METRIC_NAME = 'Metric Name'
TABLE_HEAD_INSTANCE_NAME = 'Instance Name'
TABLE_HEAD_IP = 'IP'
BY_GROUP_TABLE_HEAD = [TABLE_HEAD_GROUP_NAME,TABLE_HEAD_METRIC_NAME]
PER_INSTANCE_TABLE_HEAD = [TABLE_HEAD_GROUP_NAME,TABLE_HEAD_INSTANCE_NAME,TABLE_HEAD_IP,TABLE_HEAD_METRIC_NAME]

AWS_FEE_TABEL_HEAD = [TABLE_HEAD_METRIC_NAME]

# chart config
FUNC_TYPE_COUNT = 0
FUNC_TYPE_AVG = 1
FUNC_TYPE_MAX = 2
FUNC_TYPE_MIN = 3
FUNC_TYPE_SUM = 5


# chart type
WINDOW_CHART = 0
PAGE_CHART = 1


