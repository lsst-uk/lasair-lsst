FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip 

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ \
  python3-yaml
RUN pip3 install \
  numpy  \
  scipy
RUN pip3 install \
  confluent-kafka==1.7.0 \
  qub-sherlock==2.2.0

# Required for tests
RUN pip3 install \
  xmlrunner \
  cryptography \
  flask \
  psutil \
  coverage
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  mysql-client \
  mysql-server \
  openjdk-11-jre-headless \
  wget \
  sudo \
  swig 

# Required for Ingest
RUN pip3 install \
  cassandra-driver \
  gkdbutils \
  fastavro

# Required for filter
RUN pip3 install \
  mocpy \
  mysql-connector-python \
  ephem \
  gkhtm \
  gkdbutils \
  cassandra-driver \
  fastavro
