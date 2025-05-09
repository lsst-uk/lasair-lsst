FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv

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
  python3-coverage 
RUN pip3 install --break-system-packages \
  xmlrunner

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ \
  python3-flask \
  python3-flask-restful 
#  python3-confluent-kafka \
#  python3-yaml \
#  python3-numpy \
#  python3-scipy \
#  python3-unittest2
RUN pip3 install \
  setuptools \
  wheel \
  confluent-kafka \
  numpy \
  scipy \
  pyyaml
RUN pip3 install \
  qub-sherlock==2.3.1 --no-use-pep517

# Required for Ingest
#RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
#  python3-cassandra \
#  python3-lz4
RUN pip3 install \
  gkdbutils \
  fastavro \
  cassandra-driver \
  lz4

# Required for filter
#RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
#  python3-mysql.connector
RUN pip3 install \
  mysql-connector-python \
  mocpy \
  ephem \
  gkhtm \
  gkdbutils \
  bazinBlackBody==0.8 \
  dustmaps

# required for MMA
#RUN pip3 install --break-system-packages \
RUN pip3 install \
  skytag

# required for dustmaps
RUN python3 -c "from dustmaps.config import config;import dustmaps.sfd;config.reset();dustmaps.sfd.fetch()"
