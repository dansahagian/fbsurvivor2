DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "fbsurvivor celery worker started at ${DATE}" | systemd-cat -p info

cd /opt/fbsurvivor2
pipenv run celery -A fbsurvivor worker -l INFO