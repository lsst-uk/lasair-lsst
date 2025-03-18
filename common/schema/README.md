## Lasair Schema handling

![Screenshot](lasair-schema.png)

New plan for schema wrangling, which should take out a lot of the manual intervention that we have now whenever the Rubin schema gets updated. In the diagram, there is a flow from left to right. On the left are three kinds of input data:

- 1. object_features: This file lists the Lasair-specific object features, with docstrings, together with the section headers for presentation, and the index to be used for the MySQL table.

- 2. The five AVSC files from the [Rubin schema](https://github.com/lsst/alert_packet/tree/main/python/lsst/alert/packet/schema/7/3). These are liable to be changed without our control.

- 3. The [Lasair tables](https://github.com/lsst-uk/lasair-lsst/tree/develop/common/schema/lasair_schema) but not the MySQL:objects table. For example sherlock_classification, area_hits are MySQL tables; cutouts and diaSources are CQL tables.

These data files are versioned by the LSST schema number, and will live in a directory called for example "7.4".

These data files are transformed by three programs:

- join_object_schema: takes (1) and (2) above and builds the [objects.py](https://github.com/lsst-uk/lasair-lsst/blob/develop/common/schema/lasair_schema/objects.py) table specification

- fetch_avsc: pulls the AVSC files from github, and makes some cosmetic changes. Also changes dec to decl and adds the indexes needed to store these in Cassandra.

- make_create_table: converts the table specifications to SQL or CQL CREATE TABLE commands.

- make_alter_table: compares the table specifications of two different schema instantiations and uses the difference to make SQL or CQL ALTER TABLE commands.

### Updating the schema

- `cd lasair-lsst/commong/schema`
- Make a directory for the new schema, for example `mkdir 704`
- Fetch all the Rubin .avsc files:
```
python3 1_fetch_avsc.py 704
```
- Build the combined object for MySQL:
```
    python3 2_join_object_schema.py 704
```
- Look for required `ALTER TABLE` commands:
python3 3_make_alter_table.py sql 703 704 objects
python3 3_make_alter_table.py cql 703 704 diaForcedSources
python3 3_make_alter_table.py cql 703 704 diaNondetectionLimits
python3 3_make_alter_table.py cql 703 704 diaObjects
python3 3_make_alter_table.py cql 703 704 diaSources
python3 3_make_alter_table.py cql 703 704 ssObjects
