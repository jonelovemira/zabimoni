#! flask/bin/python

# unitest framework
import unittest

# database
from monitor import app,db

class TestCase(unittest.TestCase):

	# create database tables for every test
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/newtest'
		self.app = app.test_client()
		db.session.remove()
		db.create_all()
     
	# drop database tables during test down
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ''' tests for functions in zabbix api'''
	def test_