#!/usr/bin/env bash

pip2.7 install -r requirements.txt
if [ ! -d "data" ]; then
    mkdir data
fi
python2.7 manage.py create_db
python2.7 manage.py db init
python2.7 manage.py db migrate
python2.7 manage.py create_categories
