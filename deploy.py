#! flask/bin/python

from __future__ import with_statement
from fabric.api import local, settings, abort,run,cd,env
from fabric.contrib.console import confirm
from fabric.contrib.project import upload_project,rsync_project

env.use_ssh_config = False
env.hosts = ['10.0.2.141']
env.port = 22
env.user = 'monitor'
env.key_filename = '~/id_rsa_old.pem'


def upload():
	remote_dir = '/home/monitor/project'
	upload_project(remote_dir=remote_dir)

def rsync():
	remote_dir = '/home/monitor/project'
	rsync_project(remote_dir=remote_dir)
