from flask import Flask,g
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir, ADMINS, TMP_FILE
from flask.ext.login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import current_user
import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy.orm import sessionmaker,scoped_session
#from flask_alembic import Alembic


app = Flask(__name__)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'auth.login'

#configuration
app.config.from_object('config')

#db = SQLAlchemy(app)
db = SQLAlchemy(app,session_options={'autoflush':False})
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
# mail = Mail(app)
# db.init_app(app)


# if not app.debug:
#     import logging
#     from logging.handlers import SMTPHandler
#     credentials = None
#     if MAIL_USERNAME or MAIL_PASSWORD:
#         credentials = (MAIL_USERNAME, MAIL_PASSWORD)
#     mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'monitor failure', credentials)
#     mail_handler.setLevel(logging.ERROR)
#     app.logger.addHandler(mail_handler)

# if os.environ.get('ZBX_DATABASE_URL') is None:
#     from config import ZBX_DATABASE_URL
# else:
#     ZBX_DATABASE_URL = os.environ['ZBX_DATABASE_URL']

# engine = create_engine(ZBX_DATABASE_URL)
# Base = declarative_base(engine)
# Session = None

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    #tmp_file = '/home/monitor/project/monitor-0.3.7/tmp/monitor.log'
    tmp_file = TMP_FILE
    file_handler = RotatingFileHandler(tmp_file, 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('monitor startup')

from monitor.auth.controllers import mod_auth as auth_module
from monitor.chart.controllers import mod_chart as chart_module
from monitor.item.controllers import mod_item as item_module
from monitor.zabbix.controllers import mod_zabbix as zabbix_module
app.register_blueprint(auth_module)
app.register_blueprint(chart_module)
app.register_blueprint(item_module)
app.register_blueprint(zabbix_module)

from monitor import views,models
# db.create_all()

# @app.before_request
# def before_request():
#     g.user = current_user
#     metadata = Base.metadata
#     session_factory = sessionmaker(bind=engine)
#     localSession = scoped_session(session_factory)
#     # print Session
#     Session = localSession

# @app.teardown_request
# def teardown_request(exception):
#     print 'Session in teardown_request: ', Session
#     # Session.remove()

#if __name__ == '__main__':
    #manager.run()
