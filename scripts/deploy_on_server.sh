#!/bin/zsh

echo "Stopping services..."
sudo systemctl stop fbsurvivor.service
sudo systemctl stop celeryworker.service
sudo systemctl stop celerybeat.service

echo "Deploying..."
cd /opt/fbsurvivor2
git pull origin main
pipenv install

pipenv run ./manage.py migrate
pipenv run ./manage.py collectstatic --no-input
pipenv run ./manage.py check --deploy

echo "Starting services..."
sudo systemctl start fbsurvivor.service
sudo systemctl start celeryworker.service
sudo systemctl start celerybeat.service
