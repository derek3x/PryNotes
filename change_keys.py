#!/usr/bin/env python2
"""
This will add another encryption key.  Any new notes or resaved notes will use the new key.
The old key is not deleted as it is used to decrypt the messages already encrypted using that key.
You can do this as many times as you want.  It is all automatic.
"""
import keyczar
import os

from keyczar import keyczart

newpath = r'tmp/kz' 
keyczart.main(['addkey','--location=tmp/kz/' ,'--status=primary'])
