FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ 
RUN pip3 install \
  flask \
  flask-restful \
  confluent-kafka \
  numpy \
  scipy \
  unittest2 \
  pyyaml
RUN pip3 install \
  qub-sherlock==2.3.1

# Required for tests
RUN pip3 install \
  xmlrunner \
  psutil \
  coverage \
  cryptography 
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  mysql-client \
  mysql-server \
  openjdk-11-jre-headless \
  wget \
  sudo \
  swig 

# Required for Ingest
RUN pip3 install \
  gkdbutils \
  fastavro \
  cassandra-driver \
  lz4

# Required for filter
RUN pip3 install \
  mocpy \
  mysql-connector-python \
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
