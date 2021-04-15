#!/bin/zsh

echo "Running CI..."
if pipenv run black --check . && pipenv run pytest .
then
  "/opt/fbsurvivor2/scripts/deploy_on_server.sh"
else
  echo
  echo "Failed to deploy"
  echo
fi

echo
echo "Deployment Complete!"
echo