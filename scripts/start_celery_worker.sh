#!/bin/zsh

pipenv run celery -A fbsurvivor worker -l INFO