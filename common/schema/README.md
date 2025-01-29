## Lasair Schema handling
As of Jan 2025, this is based on the LSST 7.3 schema

https://github.com/lsst/alert_packet/tree/main/python/lsst/alert/packet/schema/7/3

The schemata for the varoious components are fetched from github. These versions contain doc strings. Getting the schems from the registry means no doc strings.
Each component becomes a Lasair schema file (LSF).
These components are written into the `lsst_schema` directory.

A LSF is a JSON-like file with these keys:
- `name`, a string
- `fields`, list of
- `type`, which can be any of float, double, int, long, bigint, date, string, bigstring, text, timestamp, JSON
- `default`, the default value
- `extra`, text to be appended to the SQL/CQL definition line
- `doc`, natural language description
- `indexes`, a set of strings to be added to the SQL/CQL `CREATE TABLE`
- `with`, a string to be added after the CREATE TABLE command

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
git rm -r lsst_schema/*
git rm lasair_schema/diaObjects.py
git rm lasair_schema/diaSources.py
git rm lasair_schema/diaForcedSources.py
git rm lasair_schema/diaNondetectionLimits.py
git rm -r lasair_sql/*
git rm -r lasair_cql/*
```
#### Fetch new schema from github
in the code `fetch_from_github.py` edit the first line to get the correct github url
and make sure the Cassandra indexes are correct
```
mkdir lsst_schema
python3 fetch_from_github.py
```
#### Sample output
```
diaForcedSource
diaNondetectionLimit
diaObject
diaSource
ssObject
```

#### Modify lasair_schema

While the directory `lsst_schema` is automatically generated, the `lasair_schema` directory has handmade changes. Start with `mkdir lasair_schema`, then  copy all in `lsst_schema` to `lasair_schema` then make changes: Specifically:

- Adding features to the relational table `objects`
  - Look at the new attributes in `lasair_schema/diaObjects.py` and decide if any should be added to the object schema. If so, edit `lasair_schema/objects.py`.
  - Then create suitable `ALTER TABLE` commands and execute these on the main database and on all the local databases associated with filter nodes.
  - You will also need to change the code in `pipeline/filter/features/diaObjectCopy.py` so that these are properly copied into the relational database.

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
git add alert-lsst.avsc lsst_schema lasair_schema lasair_cql lasair_sql
```

