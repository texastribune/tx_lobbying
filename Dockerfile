FROM ubuntu:14.04
MAINTAINER Chris <c@crccheck.com>

RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  # for data processing support
  wget unzip curl \
  # for python
  python2.7 python-dev python-pip \
  # for postgis
  libpq-dev libgeos-dev \
  # node to build static files
  nodejs nodejs-legacy npm > /dev/null
# ubuntu version of pip is buggy
RUN pip install --upgrade pip
RUN npm config set color false; \
  npm config set loglevel warn; \
  npm install -g grunt-cli --no-color

ADD requirements.txt /app/requirements.txt
RUN pip install --quiet -r /app/requirements.txt

ADD . /app
WORKDIR /app
ENV PYTHONPATH /app

# default waitress port
EXPOSE 8080

RUN npm install
RUN grunt build --no-color
RUN python example_project/manage.py collectstatic --noinput
