FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ \
  python3 \
  python3-dev \
  python3-yaml \
  python3-pip 
RUN pip3 install \
  numpy 
RUN pip3 install \
  confluent-kafka==1.7.0 \
  qub-sherlock==2.2.0

# Required for tests
RUN pip3 install \
  xmlrunner \
  cryptography
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  mysql-client \
  mysql-server \
  openjdk-11-jre-headless \
  wget \
  sudo \
  swig

# Required for filter
RUN pip3 install \
  mocpy \
  mysql-connector-python \
  ephem \
  gkhtm
