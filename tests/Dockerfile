FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip 

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Required for Sherlock
RUN apt-get update && apt-get -yq dist-upgrade && apt-get install -yq --no-install-recommends \
  gcc \
  g++ \
  python3-flask \
  python3-flask-restful \
  python3-confluent-kafka \
  python3-numpy \
  python3-scipy \
  python3-unittest2 \
  python3-yaml
RUN pip3 install \
  qub-sherlock==2.3.1

# Required for tests
#RUN pip3 install --break-system-packages \
RUN pip3 install \
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
#RUN pip3 install --break-system-packages \
RUN pip3 install \
  gkdbutils \
  fastavro 
#  cassandra-driver \

# Required for filter
#RUN pip3 install --break-system-packages \
RUN pip3 install \
  mocpy \
  mysql-connector-python \
  ephem \
  gkhtm \
  gkdbutils \
  bazinBlackBody \
  dustmaps

# required for MMA
#RUN pip3 install --break-system-packages \
RUN pip3 install \
  skytag

# required for dustmaps
RUN python3 -c "from dustmaps.config import config;import dustmaps.sfd;config.reset();dustmaps.sfd.fetch()"
