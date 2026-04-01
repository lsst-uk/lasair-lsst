# Annotaiton Filter module #
Takes batches of JSON files from the filter node, then processes them.

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

