#!/bin/zsh

systemctl stop fbsurvivor.service
systemctl stop celeryworker.service
systemctl stop celerybeat.service

git pull origin main
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input

systemctl start fbsurvivor.service
systemctl start celeryworker.service
systemctl start celerybeat.service