PryNotes
========

Web based note application. Save your ideas, notes, todo lists, recipes, news articles or anything you find online. Keep it safe and secure with encryption and in a database that won't be mined or sold.

www.prynotes.com

Difference Between the Website and the GitHub Source:
========

-Removed secret keys

-Simplified the encryption. I did this to avoid having the encryption method out. I use the keyczar still on the website, but include a special changing salt and extra security. On the github version I use just the keyczar encryption. This is simply a security thing for the website.

-This version is setup to use sqlite. Just makes it easier to test and run locally. It is a super quick change.

To Setup Locally:
========

    virtualenv --no-site-packages flask
    source flask/bin/activate
    pip install -r requirements.txt
    ./create_keys.py
    ./db_create.py
    
*if helper scripts don't run, make them executable (see Helper Scripts)

*If you have problems installing Flask-WeasyPrint.  This is due to LXML.  A quick google search will show you the extra packages you need to install for your Operating System.  It is different for each O/S. (libxml2-devel, libxslt-devel, python-devel, or python-dev)
    
To Run:

    chmod a+x run.py
    ./run.py

Browser:

    localhost:5000

Helper Scripts:
=========

Create Encryption Keys:
    
    chmod a+x create_keys.py
    ./create_keys.py
    
Create Database:

    chmod a+x db_create.py
    ./db_create.py
    
Merge Database:

-Use this if you make any changes to the models.py file

    chmod a+x db_merge.py
    ./db_merge.py
    
Change Keys (encryption keys):

-Will rotate your keys.  It keeps the old keys for decryption only, and encrypts in new keys.

    chmod a+x db_merge.py
    ./change_keys.py    
