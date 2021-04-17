DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "fbsurvivor celery worker started at ${DATE}" | systemd-cat -p info

cd /opt/fbsurvivor2
venv/bin/celery -A fbsurvivor beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler