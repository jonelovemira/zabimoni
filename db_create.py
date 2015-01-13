#! flask/bin/python

from monitor import db

db.create_all(bind=None)