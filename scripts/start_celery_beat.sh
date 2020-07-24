#!/bin/zsh

venv/bin/celery -A fbsurvivor beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler