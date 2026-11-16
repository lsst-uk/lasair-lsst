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
  unittest-xml-reporting

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

# required for webserver template render tests
RUN pip3 install \
  django \
  django-crispy-forms \
  crispy-bootstrap5 \
  django-widget-tweaks

# required for dustmaps
# HARVARD DATAVERSE RETURNS 403 TO THE PYTHON-REQUESTS USER AGENT THAT
# DUSTMAPS.SFD.FETCH() USES, SO DOWNLOAD THE TWO SFD MAPS WITH WGET AND CHECK MD5
RUN python3 -c "from dustmaps.config import config; config.reset()" \
 && SFD_DIR="$(python3 -c 'from dustmaps.std_paths import data_dir; print(data_dir())')/sfd" \
 && mkdir -p "$SFD_DIR" \
 && wget -q -O "$SFD_DIR/SFD_dust_4096_ngp.fits" https://dataverse.harvard.edu/api/access/datafile/2902687 \
 && wget -q -O "$SFD_DIR/SFD_dust_4096_sgp.fits" https://dataverse.harvard.edu/api/access/datafile/2902695 \
 && printf '%s  %s\n' \
      6f3a89528bba7d1b7bd55838da86b639 "$SFD_DIR/SFD_dust_4096_ngp.fits" \
      60f7c43d51bccaff82961de3e9f9e789 "$SFD_DIR/SFD_dust_4096_sgp.fits" \
    | md5sum -c - \
 && python3 -c "from dustmaps.sfd import SFDQuery; SFDQuery()"

RUN mkdir -p /data/mysql

# required for webserver view tests
RUN pip3 install \
  djangorestframework
# required for the webserver object-page tests (plotly is unpinned, as in deploy/roles/webserver).
# kept as the last layer so adding it reuses the cached dustmaps download above.
RUN pip3 install \
  plotly
