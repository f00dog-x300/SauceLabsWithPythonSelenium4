FROM python:3.11.2-bullseye

WORKDIR /app
COPY . /app

# installation of chrome inside container
RUN apt-get install -y wget
RUN apt-get update && apt-get upgrade -y --no-install-recommends gcc
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb -y
RUN rm *.deb

# installs pipenv
RUN pip3 install pipenv
RUN pipenv install 
CMD ["pipenv", "run", "pytest"]