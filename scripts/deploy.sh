#!/bin/zsh

if black --check . && pipenv run pytest .
then
  echo "Deploying..."
  ssh dan@fbsurvivor.com "/opt/fbsurvivor2/scripts/deploy_on_server.sh"
else
  echo
  echo "Failed to deploy"
fi