# Filter module #
Takes a Kafka stream of annotated JSON events, ingests them into a local MySQL,
finds coincidences with watchlists, runs query/filters on them, 
then pushes the local MySQL to the global relational database, via CSV files.

* `filter_runner.py`
Runs the filter.py regularly, intended primarily to be invoked by the filter service

* `filter.py`
Manages the local database connection and Kafka consumer and generally orchestrates the batch process

* `watchlists.py`
Check a batch of alerts against the cached watchlist files, and ingests the
resulting watchlist_hits into the local database

* `watchmaps.py`
Check a batch of alerts against the cached watchmap files, and ingests the
resulting watchmap_hits into the local database

* `filters.py`
Fetch and run the users active queries and produces Kafka for them


