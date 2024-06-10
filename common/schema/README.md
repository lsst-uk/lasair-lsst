## Lasair Schema handling
As of June 2024, this is based on the LSST 7 schema

https://github.com/lsst/alert_packet/tree/main/python/lsst/alert/packet/schema/7/0

The schema of the alert is fetched as a single `.avsc` file from LSST (see below).

It is split it into components with the program `avsc2lasair.py`
with each component being a Lasair schema file (LSF).

These components are written into the `lsst_schema` directory.

A LSF is a JSON-like file with these keys:
- `name`, a string
- `fields`, list of
- `type`, which can be any of float, double, int, long, bigint, date, string, bigstring, text, timestamp, JSON
- `default`, the default value
- `extra`, text to be appended to the SQL/CQL definition line
- `doc`, natural language description
- `indexes`, a set of strings to be added to the SQL/CQL `CREATE TABLE`

A LSF is not actually JSON, rather it is JSON text with the phrase `schema = ` prepended,

with a file name ending in `.py`, so that it can be imported into python code.

There may also be Lasair added-value fields in the LSF: features and attributes not present in the original LSST object.

There are other LSFs for Lasair-native data, such as `annotations`, `sherlock_classifications`, etc.

These edited versions of the LSST files, plus the additional LSFs, are kept in the `lasair_schema` directory.

The program `convert.py` can now convert any Lasair schema file into a SQL or CQL

`CREATE TABLE` statement that can be used to instantiate the tables. LSFs can also be importedto make the Schema Browser of the Lasair web and other schema tools.  

### Updating to a New Schema
#### Get the old schema out of the way
```
git rm alert-lsst.avsc dp02.avsc dp02.avsc.orig
git rm -r lsst_schema/*
git rm lasair_schema/diaObjects.py
git rm lasair_schema/diaSources.py
git rm lasair_schema/diaForcedSources.py
git rm lasair_schema/diaNondetectionLimits.py
git rm -r lasair_sql/*
git rm -r lasair_cql/*
```
#### Fetch new schema from registry
```
python3 schema_from_registry.py > alert-lsst.avsc
mkdir lsst_schema
python3 avsc2lasair.py
```
#### Sample output
```
alertId type long
diaSource record has 104 fields
prvDiaSources is null or array of diaSource
prvDiaForcedSources is null or array of diaForcedSource with 10 fields
prvDiaNondetectionLimits is null or array of diaNondetectionLimit with 4 fields
diaObject is null or has 83 fields
ssObject is null or has 53 fields
cutoutDifference is null or bytes
cutoutScience is null or bytes
cutoutTemplate is null or bytes
```
#### Add indexes in lasair_schema
```
mkdir lasair_schema
```
copy all in lsst_schema to lasair_schema then make changes:
- diaForcedSources.py: 
- `"indexes": ["PRIMARY KEY (diaObjectId,midPointMjdTai)"]`
- diaNondetectionLimits.py: 
- `"indexes": ["PRIMARY KEY (midpointMjdTai)"]`
- diaObjects.py: 
- `"indexes": ["PRIMARY KEY (diaObjectId, radecMjdTai)"]`
- diaSources.py: 
- `"indexes": ["PRIMARY KEY (diaObjectId, midPointMjdTai, `diaSourceId)"]
- ssObjects.py: 
- `"indexes": ["PRIMARY KEY (ssObjectId)"]`

#### Make CQL and SQL create table statements
```
mkdir lasair_sql
mkdir lasair_cql
python3 convert.py sql annotations
python3 convert.py sql area_hits
python3 convert.py sql crossmatch_tns
python3 convert.py cql diaForcedSources
python3 convert.py cql diaNondetectionLimits
python3 convert.py cql diaObjects
python3 convert.py cql diaSources
python3 convert.py sql mma_area_hits
python3 convert.py sql objects
python3 convert.py sql sherlock_classifications
python3 convert.py cql ssObjects
python3 convert.py sql watchlist_hits
```
#### On cassandra
```
cqlsh:lasair> drop table diaobjects;
cqlsh:lasair> drop table diasources ;
cqlsh:lasair> drop table diaforcedsources ;
cqlsh:lasair> drop table dianondetectionlimits ;
cqlsh:lasair> drop table ssobjects ;
```
Then do all the create tables from above
```
cqlsh:lasair> desc tables;
diaforcedsources  dianondetectionlimits  diaobjects  diasources  ssobjects
```
#### On ingest node
```
cd lasair-lsst/utility
python3 kafka_consumer.py --broker=lasair-lsst-dev-kafka:9092 --schema_reg=https://usdf-alert-schemas-dev.slac.stanford.edu --topic=alerts-simulated --print_one
```
keys are: alertId, diaSource, prvDiaSources, prvDiaForcedSources, prvDiaNondetectionLimits, diaObject, ssObject
```
cd lasair-lsst/pipeline/ingest
python3 ingest.py --maxalert=100
```
#### On filter node
```
cd lasair-lsst/pipeline/filter
python3 filtercore.py --maxalert=10
```
#### Make cutoutcass
```
CREATE KEYSPACE cutouts WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3 };
CREATE TABLE IF NOT EXISTS cutouts (
cutoutid  ascii,
objectId  bigint,
imjd  int,
cutoutimage blob,
PRIMARY KEY (imjd, cutoutid)
);
```
#### Put the new files in git
```
git add alert-lsst.avsc lasair_cql lasair_sql lasair_schema/
```

