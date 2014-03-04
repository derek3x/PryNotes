PryNotes
========

Web base note application. Save your ideas, or the web, and keep it safe and secure.

www.prynotes.com

Difference Between the Website and the GitHub Source:
========

-Removed secret keys

-Simplified the encryption. I did this to avoid having the encryption method out. I use the keyczar still on the website, but include a special changing salt and extra security. On the github version I use just the keyczar encryption. This is simply a security thing for the website.

-This version is setup to use sqlite. Just makes it easier to test and run locally. It is a super quick change.

To Setup Locally:
========
Run:

    python virtualenv.py flask
    
Then Install:
    
    flask/bin/pip install flask
    flask/bin/pip install flask-login
    flask/bin/pip install flask-openid
    flask/bin/pip install sqlalchemy==0.7.9
    flask/bin/pip install flask-sqlalchemy==0.16
    flask/bin/pip install sqlalchemy-migrate==0.7.2
    flask/bin/pip install flask-whooshalchemy==0.55a
    flask/bin/pip install flask-wtf==0.8.4
    flask/bin/pip install beautifulsoup
    flask/bin/pip install Image
    flask/bin/pip install python-keyczar --pre
    
Create Encryption Keys:
    
    chmod a+x create_keys.py
    ./create_keys.py
    
Create Database:

    chmod a+x db_create.py
    ./db_create.py

To Run:

    chmod a+x run.py
    ./run.py

Browser:

    localhost:5000

To Do:
=========
    -Shared Notebooks/Notes
