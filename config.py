import os
basedir = os.path.abspath(os.path.dirname(__file__))


if os.environ.get('DATABASE_URL2') is None:
    SQLALCHEMY_DATABASE_URI = 'mysql://monitor:monitor@127.0.0.1/monitor2'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL2']

SQLALCHEMY_POOL_RECYCLE = 3600
    
# SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/testDatabase'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# mail server settings
MAIL_SERVER = 'smtp.tp-link.net'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'xuzhongyong'
MAIL_PASSWORD = 'minmin520'
MAIL_DEFAULT_SENDER = 'xuzhongyong@tp-link.net'

# administrator list
ADMINS = ['xuzhongyong@tp-link.net']

# path of tmp file for log
TMP_FILE = '/home/monitor/project/monitor-0.3.7/tmp/monitor.log'
