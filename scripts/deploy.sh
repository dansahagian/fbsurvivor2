#!/bin/zsh

sudo systemctl stop fbsurvivor.service
sudo systemctl stop celeryworker.service
sudo systemctl stop celerybeat.service

git pull origin main
rm -rf venv
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input

sudo systemctl start fbsurvivor.service
sudo systemctl start celeryworker.service
sudo systemctl start celerybeat.service