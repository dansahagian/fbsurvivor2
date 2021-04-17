#!/bin/zsh

echo "Stopping services..."
sudo systemctl stop fbsurvivor.service
sudo systemctl stop celeryworker.service
sudo systemctl stop celerybeat.service

echo "Deploying..."
cd /opt/fbsurvivor2
git pull origin main
venv/bin/pip install -r ./requirements/production.txt

./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --no-input
./venv/bin/python manage.py check --deploy

echo "Starting services..."
sudo systemctl start fbsurvivor.service
sudo systemctl start celeryworker.service
sudo systemctl start celerybeat.service
