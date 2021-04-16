#!/bin/zsh
pipenv run celery -A fbsurvivor_dev worker -l INFO