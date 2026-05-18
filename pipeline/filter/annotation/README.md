# Annotaiton Filter module #
Takes batches of JSON files from the filter node, then processes them.

Annotations are stored in the database during repeated calls to `ingest_message_list`. In addition
lists are kept of diaObjects that are affected by each annotation of the batch.
In this structure, "fruitbat" is an annotator, and the numbers are diaObjectId:
`ann_diaObject = {'fruitbat':[313853517837107288, 313853517837107277, ...]}`

In the `post_ingest` phase, the filters are run.
Using the `ann_diaObject` information, we build the SQL queries for 
filters affected by these annotations. For example:

`SELECT <selected> WHERE <constraint> AND diaObjectId IN (313853517837107288, 313853517837107277, ...)`

Provided methods:
* `setup`
To get the annotation filter ready to start.

* `setup_batch`
To get ready for a fresh batch of alerts.

* `ingest_message_list`
Deal with a list of JSON messages, in this case annotations.
Ingests the data into the local database.

* `post_ingest`
After the annotations are stored in the local database,
run all the user filters.

