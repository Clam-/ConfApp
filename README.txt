ConfApp README
==================

Getting Started
---------------

- export VENV=~/env

- cd <directory containing this file>

- $VENV/bin/python setup.py develop

- $VENV/bin/initialize_ConfApp_db development.ini

- $VENV/bin/pserve development.ini

- uwsgi --ini-paste development.ini

Note to self
------------
git fetch --all
git reset --hard origin/master

to sync remote copies back to original


Reset process:
--------------
rm ConfApp.sqlite
~/env/bin/initialize_ConfApp_db development.ini
~/env/bin/uwsgi --ini-paste development.ini
