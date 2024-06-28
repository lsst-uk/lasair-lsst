# Fetching DP03 for Adler
## schema

#### process the schema
- Get YAML [from here](https://raw.githubusercontent.com/lsst/sdm_schemas/main/yml/dp03_10yr.yaml), then convert to AVSC then to Lasair format
```
python3 yaml2avsc.py < dp03_10yr.yaml > dp03.avsc
mkdir lsst_schema
python3 avsc2lasair.py dp03.avsc
cp -R lsst_schema lasair_schema
```
#### modify the schema
- Change the lasair schema so the "indexes" has
```
SSObjects: PRIMARY KEY (ssObjectId)
MPCORBs:   PRIMARY KEY (ssObjectId)
DiaSources:PRIMARY KEY (ssObjectId, diaSourceId)
SSSources: PRIMARY KEY (ssObjectId, diaSourceId)

"PRIMARY KEY (ssObjectId, midPointMjdTai)" or
"PRIMARY KEY (ssObjectId)" or
"PRIMARY KEY (ssSourceId)"
```
- change all the "timestamp" to "double"
- change "dec" to "decl"

#### make CQL statements in lasair_cql directory
```
python3 convert.py cql DiaSources
python3 convert.py cql MPCORBs
python3 convert.py cql SSObjects
python3 convert.py cql SSSources
```
 - Make the tables in Cassandra
```
ssh lasair-lsst-cassandra
create keyspace if not exists adler WITH replication = {'class':'SimpleStrategy', 'replication_factor':3 };
use adler;
```
run 4 create table statements from `lasair_cql` directory

## Fetch Data
- prerequisites
To fetch data you will need your `RSP_TOKEN` in the `settings.py`
```
pip3 install confluent_kafka
pip3 install cassandra_driver
pip3 install gkdbutils
```
- get alerts from data.lsst.cloud. Last two arguments are MJD start and MJD end
```
python3 tap.py data 60300 60301
```
- send the data up to kafka, using topic `adler_temp`
```
python3 json_to_kafka.py data/data_60300_60301 adler_temp
```
- put alert packets into adler keyspace
```
python3 json_to_cassandra.py data/data_60300_60301
```
- if you like you can read it back. See code for arguments.
```
python3 test_read_kafka.py --topic=adler_temp --print_one --group_id=LASAIR5
python3 test_read_cassandra.py 5012019210990749295
