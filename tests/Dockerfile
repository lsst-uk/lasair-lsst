FROM ubuntu:24.04

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
  python3-flask \
  python3-flask-restful \
  python3-confluent-kafka \
  python3-numpy \
  python3-scipy \
  python3-unittest2
RUN pip3 install --break-system-packages \
  pyyaml<=6 \
  qub-sherlock==2.2.0

# Required for tests
RUN pip3 install --break-system-packages \
  xmlrunner 
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  mysql-client \
  mysql-server \
  openjdk-11-jre-headless \
  wget \
  sudo \
  swig \
  python3-psutil \
  python3-coverage \
  python3-cryptography

# Required for Ingest
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3-cassandra \
  python3-lz4 
RUN pip3 install --break-system-packages \
  gkdbutils \
  fastavro 
#  cassandra-driver \

# Required for filter
RUN pip3 install --break-system-packages \
  mocpy \
  mysql-connector-python \
  ephem \
  gkhtm \
  gkdbutils \
  bazinBlackBody \
  dustmaps

# required for MMA
RUN pip3 install --break-system-packages \
  skytag

# required for dustmaps
RUN python3 -c "from dustmaps.config import config;import dustmaps.sfd;config.reset();dustmaps.sfd.fetch()"
