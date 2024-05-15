### Fetching DP03 for Adler
The [DP0.3 data release](https://dp0-3.lsst.io/) consists of a schema and the data. 

Get alerts from data.lsst.cloud
  python3 tap.py data 60300 60301 

Send up to kafka
  python3 json_to_kafka.py data/data_60300_60301 adler_temp

Read it back
  python3 test_read_kafka.py --topic=adler_temp --print_one --group_id=LASAIR5

Schema
  fetch yaml schema
  https://raw.githubusercontent.com/lsst/sdm_schemas/main/yml/dp03_10yr.yaml

  python3 yaml2avsc.py < dp03_10yr.yaml > dp03.avsc
  mkdir lsst_schema
  python3 avsc2lasair.py dp03.avsc
  cp -R lsst_schema lasair_schema
  -- change the lasair schema so the "indexes" has
    "PRIMARY KEY (ssObjectId, midPointMjdTai)" or
    "PRIMARY KEY (ssObjectId)"
  -- change all the "timestamp" to "double"

Cassandra
  make CQL statements in lasair_cql directory
  python3 convert.py cql DiaSources
  python3 convert.py cql MPCORBs
  python3 convert.py cql SSObjects
  python3 convert.py cql SSSources

  ssh lasair-lsst-cassandra
  create keyspace if not exists adler WITH replication = {'class':'SimpleStrategy', 'replication_factor':3 };
  use adler;
    run 4 create table statements from lasair_cql directory

On svc node
  pip3 install cassandra_driver
  pip3 install gkdbutils

  python3 json_to_cassandra.py data/data_60300_60301 adler_temp

