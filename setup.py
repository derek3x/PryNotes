#!/usr/bin/python2
import os, subprocess, sys
subprocess.call(['python', 'virtualenv.py', 'flask'])
if sys.platform == 'win32':
    bin = 'Scripts'
else:
    bin = 'bin'
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-login'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-openid'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy==0.7.9'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-sqlalchemy'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy-migrate'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-whooshalchemy'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-wtf'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'beautifulsoup'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'Image'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'python-keyczar', '--pre'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'Flask-WeasyPrint'])
subprocess.call([os.path.join('flask', bin, 'python'), 'create_keys.py'])
subprocess.call([os.path.join('flask', bin, 'python'), 'db_create.py'])
