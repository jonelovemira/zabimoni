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

COMMAND_FOLDER = '/command'

# different path
GENERATE_REPORT_PATH = basedir + COMMAND_FOLDER + '/generate_report.py '
TMP_FILE = basedir + '/tmp/monitor.log'
REMOTE_COMMAND_LOG = basedir + '/tmp' + '/remote_command'
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

AUTOSCALE_COMMAND_PATH = basedir + COMMAND_FOLDER + '/autoscale_group.py'

EMAIL_SNS_PATH = basedir + '/sendemail_alarm.py'
EMAIL_SNS_NEW_PATH = basedir + COMMAND_FOLDER + '/sendemail_alarm.py'

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
	'zabbix': ZBX_DATABASE_URL
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
GENERATE_REPORT_SCRIPT_PATH = basedir + '/'

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
TABLE_HEAD_ALIAS = 'Alias'
TABLE_HEAD_DESCRIPTION = 'Description'
TABLE_HEAD_INSTANCE_NAME = 'Instance Name'
TABLE_HEAD_IP = 'IP'
TABLE_HEAD_AVAILABILITY = 'Availability'
BY_GROUP_TABLE_HEAD = [TABLE_HEAD_GROUP_NAME,TABLE_HEAD_METRIC_NAME,TABLE_HEAD_ALIAS, TABLE_HEAD_DESCRIPTION]
PER_INSTANCE_TABLE_HEAD = [TABLE_HEAD_GROUP_NAME,TABLE_HEAD_INSTANCE_NAME,TABLE_HEAD_IP,TABLE_HEAD_METRIC_NAME,TABLE_HEAD_AVAILABILITY,TABLE_HEAD_ALIAS, TABLE_HEAD_DESCRIPTION]

AWS_FEE_TABEL_HEAD = [TABLE_HEAD_METRIC_NAME]

NO_FEE_RESULT_SET = [BY_GROUP_RESULT,PER_INSTANCE_RESULT]

# chart config
FUNC_TYPE_COUNT = 0
FUNC_TYPE_AVG = 1
FUNC_TYPE_MAX = 2
FUNC_TYPE_MIN = 3
FUNC_TYPE_SUM = 5


# chart type
WINDOW_CHART = 0
PAGE_CHART = 1

# SNS operation args label
SNS_TOPIC_NAME_LABEL = 'Topic Name'
SNS_SEND_SNS_2_LABLE = 'Send Notification to'

# ASG operation args label
ASG_FROM_GROUP_LABEL = 'From the group'
ASG_ACTION_TYPE_LABEL = 'Take this action'
ASG_ACTION_NUMBER = 'Instance number'

## Operation name
SNS_OPERATION_NAME = 'Notification by Mail'
ASG_OPERATION_NAME = 'Auto Scaling Action'
SNS_OPERATION_ATTR = [SNS_TOPIC_NAME_LABEL,SNS_SEND_SNS_2_LABLE]
ASG_OPERATION_ATTR = [ASG_FROM_GROUP_LABEL,ASG_ACTION_TYPE_LABEL]
ASG_SCALE_UP = 'Up'
ASG_SCALE_DOWN = 'Down'

MAX_INIT_POINTS = 3600
CHART_INIT_DEFAULT_MESSAGE = 'chart load successfully'

AREA_PROXY_SPLITER = '__'

ZABBIX_TEMPLATE_PREFIX = 'Template'
TEMPLATE_GROUP_SPLITER = '__monitor__'
NORMAL_TEMPLATE_NAME = ZABBIX_TEMPLATE_PREFIX + '__normal'


PROTOTYPE_COMMAND_PATH = basedir + COMMAND_FOLDER + '/add_net_metric_disable_trigger.py' + ' ' + '--instanceip={HOST.NAME1}' + ' ' + '--metricname={ITEM.KEY1}'
AR_COMMAND_PATH = basedir + COMMAND_FOLDER +  '/rename_link_add_update_instance.py' + ' ' + '--instanceip={HOST.IP}'
UNREACHABLE_ACTION_PATH = basedir + '/sendemail_normal' + ' ' + '--content="{HOST.NAME} is unreachable for 5 minutes"'
UNREACHABLE_ACTION_PATH_2 = basedir + COMMAND_FOLDER + '/unreachable_instance_trigger.py' + ' ' + '--instanceip={HOST.NAME}'

AUTO_REGISTRATION_NAME = 'AWS auto registration'
ADD_NET_TRIGGER_NAME = 'add_net_key'
UNREACHABLE_ACTION_NAME = 'agent is unreachable'
TRIGGER_PROTOTYPE_EXPRESSION = '{Template OS Linux:net.if.in[{#IFNAME}].last()}>-1'
OS_LINUX_TEMPLATEID = '10001'
# unreachable_action_name

ZBX_TEMPLATE_CONF_FILE = basedir + '/zbx_config' + '/zbx_export_templates.xml'


DEPRECATE_TAG = '(Deprecate)'

AWS_BILLING_COMMAND_FOLDER = basedir + '/aws_fee/'
AWS_BILLING_GET_S3_FILE_C = AWS_BILLING_COMMAND_FOLDER + 'get_file_from_s3.py'
AWS_BILLING_PARSE_FILE_C = AWS_BILLING_COMMAND_FOLDER + \
    'read_from_csv_save_2_db.py'
AWS_BILLING_CSV_FOLDER = AWS_BILLING_COMMAND_FOLDER + 'csv'
BASEDIR = basedir

NORMAL_BCD_TYPE = 0
CORE_BCD_TYPE = 1
ERROR_BCD_TYPE = 2
GET_BCD_SPLITER = '@@@'

CLEAR_UNREACHABLE_HOST = basedir + '/command/clear_old_host.py --instanceip={HOST.NAME}'
UPDATE_ASG_COUNT = basedir + '/command/asg_instance_count_update.py'
UPDATE_O_DATA_PATH = basedir + '/command/update_operational_data.py'