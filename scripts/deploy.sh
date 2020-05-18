#!/bin/zsh

git pull origin master
pipenv install
pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --no-input
pipenv run gunicorn fbsurvivor.wsgi
