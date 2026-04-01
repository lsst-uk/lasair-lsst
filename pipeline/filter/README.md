# Filter module #
Takes a Kafka stream of JSON messages, 
and database connections, etc, and makes them available to 
syntax-specific services in subdirectories/subclasses.

* `filter_runner.py`
Runs the filter.py regularly, intended primarily to be invoked by the filter service

* `filtercore.py`
Manages the local database connection and Kafka consumer and generally orchestrates the batch process. Expects find a subdirectory/subclass with the methods setup, setup_batch, ingest_message_list, post_ingest.

* `ingest_message_list`
Ingests the messages into a database.

* `post_ingest
Runs all the filters.
For alerts, also finds coincidences with watchlists, runs query/filters on them, 
then pushes the local MySQL to the global relational database, via CSV files.

