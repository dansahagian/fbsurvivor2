#!/bin/zsh

echo "Running CI..."

cd /opt/pre_deploy
git clone git@github.com:dansahagian/fbsurvivor2.git
cd fbsurvivor2
pipenv --rm
pipenv install --dev

if pipenv run black --check . && pipenv run pytest .
then
  echo "Deploying..."
  cd /opt/fbsurvivor2
  git pull origin main
  pipenv --rm
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
fi

