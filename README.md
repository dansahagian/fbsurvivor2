
[![Python 3.8](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3111/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

# FB Survivor
This project is used to run a family and friends NFL Survivor League. The league was originally managed using email and Excel. The first version of the application was written in Python, Flask, and used MongoDB. The second version switched to using Postgres and raw SQL queries, but continued to use Flask. This version, technically the third (but with 2 in the name), is a ground up rewrite using Django and leveraging Django's ORM.

## About the Deployment
- Runs on a single [Linode](https://www.linode.com/) running Debian Linux
- Deployed with a simple deploy script
- Async tasks (reminders) with Celery and Celery Beat
- Redis is used for caching and the Celery queue
