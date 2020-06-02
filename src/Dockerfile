FROM python:3.6.9

# python envs
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
COPY . /code
WORKDIR /code

RUN pip install -r requirements.txt
