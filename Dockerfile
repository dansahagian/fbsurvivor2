FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y postgresql libpq-dev gcc nano
RUN pip install --upgrade pip
RUN pip install pip-tools

RUN useradd -ms /bin/bash survivor
USER survivor

COPY ./requirements /code/requirements
RUN pip install -r /code/requirements/dev.txt

COPY ./manage.py /code/manage.py
COPY ./fbsurvivor /code/fbsurvivor
