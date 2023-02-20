FROM python:3.11.1-bullseye

WORKDIR /code

ADD . /code

RUN pip3 install pipenv
RUN pipenv install --dev --ignore-pipfile