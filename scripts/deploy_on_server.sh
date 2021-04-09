#!/bin/zsh

echo "Running CI..."

cd /opt/pre_deploy/fbsurvivor2
git pull origin main
pipenv install --dev

if pipenv run black --check . && pipenv run pytest .
then

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

  sudo systemctl start fbsurvivor.service
  sudo systemctl start celeryworker.service
  sudo systemctl start celerybeat.service
else
  echo
  echo "Failed to deploy"
  echo
fi

echo
echo "Deployment Complete!"
echo
