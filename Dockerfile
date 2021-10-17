FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y postgresql libpq-dev gcc nano

RUN useradd -ms /bin/bash survivor
USER survivor

WORKDIR /home/survivor

COPY requirements/base.txt .
COPY requirements/production.txt .
RUN pip install --upgrade pip
RUN pip install -r production.txt
RUN pip install django-debug-toolbar==3.2.1

COPY . .

EXPOSE 8000

ENTRYPOINT ["python", "manage.py", "runserver"]