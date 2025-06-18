FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  python3-setuptools \
  python3-wheel \
  python3-packaging

# Required for tests
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  mysql-client \
  mysql-server \
  openjdk-11-jre-headless \
  wget \
  sudo \
  swig \
  python3-psutil \
  python3-cryptography \
  python3-coverage \
  python3-unittest2

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install \
  xmlrunner

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ \
  python3-flask \
  python3-flask-restful \
  python3-confluent-kafka \
  python3-yaml \
  python3-numpy \
  python3-scipy 
RUN pip3 install \
  qub-sherlock==2.3.1 --no-use-pep517

# Required for Ingest
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3-cassandra \
  python3-lz4
RUN pip3 install \
  gkdbutils \
  fastavro 

# Required for filter
#RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
#  python3-mysql.connector
RUN pip3 install \
  mysql-connector-python \
  mocpy \
  ephem \
  gkhtm \
  gkdbutils \
  bazinBlackBody>=0.8\
  dustmaps

# required for MMA
RUN pip3 install \
  skytag

# required for dustmaps
RUN python3 -c "from dustmaps.config import config;import dustmaps.sfd;config.reset();dustmaps.sfd.fetch()"

# ensure mysql tmp dir exists and is writable
RUN mkdir -p /data/mysql && chmod 777 /data/mysql

