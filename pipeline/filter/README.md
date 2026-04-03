# Filter module #
Takes a Kafka stream of JSON messages, 
and database connections, etc, and makes them available to 
syntax-specific services in subdirectories/subclasses.
The new concept is "grist", what kind of data is being processed by the filter infrastructure.
There are implementations for Rubin alerts, annotations, and testing.

* `filter_runner.py`
Runs the filter.py regularly, intended primarily to be invoked by the filter service

* `filtercore.py`
Manages the local database connection and Kafka consumer and generally orchestrates the batch process. 
Provides utility methods for sending kafka, email etc.
Expects find a subdirectory/subclass with the methods setup, setup_batch, ingest_message_list, post_ingest.

* `ingest_message_list`
Ingests the messages into a database.

* `post_ingest`
For both alerts and annotations: runs all the filters.
For alerts, also finds coincidences with watchlists, runs query/filters on them, 
then pushes the local MySQL to the global relational database, via CSV files.

Some example scripts:
- To look at the stream
```
python3 filtercore.py --maxmessage=10 --maxbatch=1 --topic_in=fast_annotations --group_id=bla46 --grist=testing
python3 filtercore.py --maxmessage=10 --maxbatch=1 --topic_in=fast_annotations --group_id=bla46 --grist=testing --verbose=True
```

- Responding to a stream of annotations
```
python3 filtercore.py --maxmessage=10 --maxbatch=1 --topic_in=fast_annotations --group_id=bla46 --grist=annotation
```

- Responding to a Rubin-Sherlock alert stream
```
python3 filtercore.py --maxmessage=10 --maxbatch=1 --group_id=bla46 --grist=alert
```

