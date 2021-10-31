FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y postgresql libpq-dev gcc nano

RUN useradd -ms /bin/bash survivor
USER survivor

WORKDIR /code

COPY ./requirements requirements
RUN pip install --upgrade pip
RUN pip install -r ./requirements/development.txt

COPY ./manage.py manage.py
COPY ./fbsurvivor fbsurvivor

