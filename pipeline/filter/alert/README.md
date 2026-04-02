# Alert Filter module #
Takes batches of JSON files from the filter node, then processes them.

Provided methods:
* `setup`
To get the alert filter ready to start.

* `setup_batch`
To get ready for a fresh batch of alerts.

* `ingest_message_list`
Deal with a list of JSON messages, in this case alerts.
Ingests the data into the local database.

* `post_ingest`
After the alerts are stored in the local database,
orchestrate database, features, watchlists etc 
run all the user filters, then push the local to the main database.

