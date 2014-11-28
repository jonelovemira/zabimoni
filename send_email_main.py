#! /home/jone/flask_project/monitor-0.3.4/flask/bin/python

import requests

if __name__ == '__main__':
	r = requests.get('http://192.168.221.130:5001/chart/sendemail/')
