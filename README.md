[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-382/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
# FB Survivor
This project is used to run a family and friends NFL survivor league. As of September 2020, it is live in "production" running on a single [Linode](https://www.linode.com/). The league was originally managed using email and Excel. The first version of the application was written in Python, Flask, and used MongoDB. The second version switched to using Postgres and raw SQL queries, but continued to use Flask. This version, technically the third (but with 2 in the name), is a ground up rewrite using Django and leveraging Django's ORM. The database is still Postgres.

This version includes:
* ~~CI/CD with CircleCI~~ A simple deploy script
* Async with Celery & ~~RabbitMQ~~ Redis
* Caching with Redis
* A minimal test suite with Pytest
