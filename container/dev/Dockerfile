# BASE
FROM python:3.9.19

# OS
RUN apt update && apt upgrade -y

# gettext
RUN apt install gettext -y


# PIP
WORKDIR /code
COPY container/dev/requirements.txt /code

RUN pip install -r requirements.txt


# SRC
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# COPY src/ .
