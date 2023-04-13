All this is based on the LSST 4.0 schema
https://github.com/lsst/alert_packet/tree/main/python/lsst/alert/packet/schema/4/0

The schema of the alert is fetched as a single `.avsc` file from LSST.
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

There may also be Lasair added-value fields in the LSF: features and
attributes not present in the original LSST object.

There are other LSFs for Lasair-native data, such as `annotations`, 
`sherlock_classifications`, etc.

These edited versions of the LSST files, plus the additional LSFs, 
are kept in the `lasair_schema` directory.

The program `convert.py` can now convert any Lasair schema file into a SQL or CQL 
`CREATE TABLE` statement that can be used to instantiate the tables. LSFs can also be imported
to make the Schema Browser of the Lasair web and other schema tools.
