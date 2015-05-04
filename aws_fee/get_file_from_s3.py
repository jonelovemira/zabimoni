#! /usr/bin/python

import time

from boto.s3.connection import S3Connection

FILENAME_FILTER = 'aws-billing-csv'
TIME_VALID = 86400
AWS_ACCESS_KEY_ID = 'AKIAI3ICECLZMJ53SDCQ'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'tplink-detailed-billing-reports'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

def str_2_clock(time_str):
    if time_str is None or time_str == '':
        raise Exception('Invalid input of str_2_clock')
    format = '%Y-%m-%dT%H:%M:%S'
    return time.mktime(time.strptime(time_str,format))

def save_file():

    con = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,\
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    bucket = con.get_bucket(BUCKET_NAME)

    for key in bucket.get_all_keys():
        if FILENAME_FILTER in key.name and str_2_clock(key.last_modified[0:18])\
            > time.time() - TIME_VALID:
            key.get_contents_to_filename(basedir + '/csv/' + key.name)

if __name__ == '__main__':
    save_file()



