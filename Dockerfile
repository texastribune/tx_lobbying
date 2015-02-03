FROM ubuntu:14.04
MAINTAINER Chris <c@crccheck.com>

RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  # for python
  python2.7 python-dev python-pip \
  # for postgis
  libpq-dev libgeos-dev \
  # node to build static files
  nodejs nodejs-legacy npm > /dev/null
RUN npm config set color false; npm install -g grunt-cli --no-color

ADD . /app
WORKDIR /app
ENV PYTHONPATH /app

# default waitress port
EXPOSE 8080

RUN pip install -r /app/requirements.txt
RUN npm install --no-color
RUN grunt build --no-color
RUN python example_project/manage.py collectstatic --noinput
