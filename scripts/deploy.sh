#!/bin/zsh

pipenv install
pipenv run ./manage migrate
pipenv run ./manage collectstatic --no-input
pipenv run gunicorn fbsurvivor.wsgi
