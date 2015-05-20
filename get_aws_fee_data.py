#! flask/bin/python

import urllib2, json, sys, StringIO, gzip, urllib


httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
opener = urllib2.build_opener(httpHandler, httpsHandler)
urllib2.install_opener(opener)


try:
    data = {
        'redirect_uri' : 'https://console.aws.amazon.com/console/home?' + \
        'nc2=h_m_mc&state=hashArgs%23&isauthcode=true',
        'client_id' : 'arn:aws:iam::015428540659:user/homepage',
        'forceMobileApp' : '',
        'forceMobileLayout' : '',
        'isIAMUser' : '1',
        'mfaLoginFailure' : '',
        'Action': 'login',
        'RemainingExpiryPeriod' : '',
        'account' : 'tplink',
        'username' : 'xuzhongyong',
        'password' : 'minmin520',
        'mfacode' : '',
        'next_mfacode' : ''
    }
    header = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;' + \
             'q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control' : 'max-age=0',
        'Connection' : 'keep-alive',
        'Content-Length' : str(len(data)),
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Host' : 'signin.aws.amazon.com',
        'Origin' : 'https://signin.aws.amazon.com',
        'Referer' : 'https://signin.aws.amazon.com/oauth?SignatureVersion=4' + \
            '&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=' + \
            'AKIAJMOATPLHVSJ563XQ&X-Amz-Date=2015-04-21T06%3A57%3A' + \
            '20.862Z&X-Amz-Signature=8d84df4b53aeabcbe244793c6606809bee' + \
            'bd9dc52dfe5452a26baf1428419ae0&X-Amz-SignedHeaders=host&' + \
            'client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fhomepage' + \
            '&redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2F' + \
            'console%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue' + \
            '&response_type=code&state=hashArgs%23',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64)' + \
        ' AppleWebKit/537.36 (KHTML, like Gecko)' + \
        ' Chrome/41.0.2272.118 Safari/537.36'
    }
    
    data = urllib.urlencode(data)

    req = urllib2.Request(
        url = 'https://signin.aws.amazon.com/oauth',
        data = data,
        headers = header
    )

    response = urllib2.urlopen(req)
    # print response.read()
except Exception, e:
	raise e