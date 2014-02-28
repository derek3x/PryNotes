#!flask/bin/python
import keyczar
from keyczar import keyczart
keyczart.main(['create','--location=tmp/kz/','--purpose=crypt','--name=PryNotes'])
keyczart.main(['addkey','--location=tmp/kz/' ,'--status=primary'])
