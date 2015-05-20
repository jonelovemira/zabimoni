#! /usr/bin/python

import requests, urllib, urllib2, cookielib, StringIO, gzip

url = 'https://tplink.signin.aws.amazon.com/console'
auth_url = 'https://signin.aws.amazon.com/oauth'

s = requests.Session()

r = s.get(url)

r = s.get(r.url + '?&state=hashArgs%23')

data = {
	'redirect_uri':'https%3A%2F%2Fconsole.aws.amazon.com%2Fconsole%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue',
	'client_id':'arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fhomepage',
	'forceMobileApp':'',
	'forceMobileLayout':'',
	'isIAMUser':'1',
	'mfaLoginFailure':'',
	'Action':'login',
	'RemainingExpiryPeriod':'',
	'account':'tplink',
	'username':'xuzhongyong',
	'password':'minmin520',
	'mfacode':'',
	'next_mfacode':'',
}

r = s.post(auth_url, data=data)
print r