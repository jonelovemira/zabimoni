from flask import Flask
# from base import db
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, TMP_FILE
from flask.ext.login import LoginManager
import os
# from flask.ext.mail import Mail



app = Flask(__name__)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'auth.login'

#configuration
app.config.from_object('config')

db = SQLAlchemy(app)
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
app.register_blueprint(auth_module)
app.register_blueprint(chart_module)
app.register_blueprint(item_module)

from monitor import views,models
# db.create_all()