PryNotes
========

Web base note application.  Save your ideas, or the web, and keep it safe and secure.

www.prynotes.com

Difference between website and github source:

-Removed secret keys

-Simplified the encryption.  I did this to avoid having the encryption method out.  I use the keyczar still on the website, but include a special changing salt as well.  On the github version I use just the keyczar encryption.  This is simply a security thing.

