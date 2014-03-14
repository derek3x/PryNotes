#!/usr/bin/env python2
import keyczar
import os
from keyczar import keyczart
newpath = r'tmp/kz' 
if not os.path.exists(newpath): os.makedirs(newpath)
keyczart.main(['create','--location=tmp/kz/','--purpose=crypt','--name=PryNotes'])
keyczart.main(['addkey','--location=tmp/kz/' ,'--status=primary'])
