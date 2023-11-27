### Fetching DP0.2 data from RSP, and its YAML schema, and pushing to Lasair Kafka
```
cd ~/lasair-lsst/utility/DP02
```
Now convert DC02 schema to what Lasair needs
```
cd schema
curl -o dp02_dc2.yaml "https://raw.githubusercontent.com/lsst/sdm_schemas/main/yml/dp02_dc2.yaml"
```

Convert the YAML to an AVRO schema
```
python3 yaml2avsc.py < dp02_dc2.yaml > dp02.avsc
```

Make the files that Lasair needs for its databases (SQL and CQL), as well as for the schema browser
```
mkdir lsst_schema
python3 ../../../common/schema/avsc2lasair.py dp02.avsc
cp lsst_schema/DP02_DiaObjects.py               lasair_schema/DP02_diaObjects.py
cp lsst_schema/DP02_DiaSources.py               lasair_schema/DP02_diaSources.py
cp lsst_schema/DP02_ForcedSourceOnDiaObjects.py lasair_schema/DP02_diaForcedSources.py
```

Now edit `lasair_schema/*.py` to add primary key to "indexes" -- examples [here](https://github.com/lsst-uk/lasair-lsst/tree/main/common/schema/lasair_schema)

Now convert these modified schema to the database CREATE TABLE
```
cp ../../../common/schema/convert.py .
python3 convert.py cql DP02_diaObjects
python3 convert.py cql DP02_diaSources
python3 convert.py cql DP02_diaForcedSources
```

Can now use the CQL to make Cassandra tables and the SQL to make Galera tables

### Get data RSP --> Lasair Kafka
Get some data via TAP interface (slow). First put your RSP token in `settings.py` as
```
RSP_TOKEN = 'gt-ZhwzwDmLzxxxxxxxxxxxxxxxxxxxxxxxxx7TJMl_gw'
```

Now make a JSON file for each object and for its diaSources and diaForcedSources. First argument is how many objects, next is minimum number of sources per object
```
python3 tap.py <howMany> <howManySources>
```

Turn it into schemaless avro packets. This directory is for howMany=5 and howManySources=10
```
python3 dp02_to_avro.py  data_0005_10
```

Push it into Lasair Kafka ready for ingestion, with topic `DP02`
```
python3 avro_to_kafka.py data_0005_10
```


