DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "fbsurvivor started at ${DATE}" | systemd-cat -p info

cd /opt/fbsurvivor2
venv/bin/gunicorn fbsurvivor.wsgi