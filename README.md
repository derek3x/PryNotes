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

Easy Way:

This will setup a virtual python environment (virtualenv.py) named "flask".  It will then install the needed
requirements and run scripts to create the database and encryption keys for your own environment.

    python setup.py

To Run:

    chmod a+x run.py
    ./run.py

Browser:

    localhost:5000
    
*If you have problems installing Flask-WeasyPrint.  This is due to LXML.  A quick google search will show you the extra packages you need to install for your Operating System.  It is different for each O/S.

Scripts:
=========

Create Encryption Keys (setup script already did this):
    
    chmod a+x create_keys.py
    ./create_keys.py
    
Create Database (setup script already did this):

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