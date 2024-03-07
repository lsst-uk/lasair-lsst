# Filter module #
Takes a Kafka stream of annotated JSON events, ingests them into a local MySQL,
finds coincidences with watchlists, runs query/filters on them, 
then pushes the local MySQL to the global relational database, via CSV files.

* runner.py
Runs the filter.py regularly, in a screen for continuous ingestion

* start_batch.py
Sets up the local database and Kafka consumer ready for a new batch

* run_batch.py
Runs all the things below

  * consume_alerts.py
Runs the Kafka consumer, can be multi-process. For each alert, 
it calls features.py for lightcurve features, then pushes the 
objects and sherlock_crossmatches to the local database

    * features.py
Computes object features and builds the INSERT query

  * watchlists.py
Check a batch of alerts against the cached watchlist files, and ingests the
resulting watchlist_hits into the local database

  * watchmaps.py
Check a batch of alerts against the cached watchmap files, and ingests the
resulting watchmap_hits into the local database

  * filters.py
Fetch and run the users active queries and produces Kafka for them

* end_batch.py
Writes statistics, sends local database to main

  * output_csv.sql
Builds CSV files from the local database, to be scp'ed to the master (lasair-db)
and ingested there.


