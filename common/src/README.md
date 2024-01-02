## The `manage_status` module

To store metrics about the progress of the ingestion pipeline.  Each set of metrics is distinguished by a `file_id`, so there can be many such sets.  In the current Lasair pipeline, this is generally the `nid` or night ID, so that a set of metrics is gathered for each night of alert ingestion. Below are the places it is used and the meaning of the keys that are used.  Some of the quantities are **set** by the code, and some are **add**. The former is a replacement value, the latter is an increment. 

Data files are in `/mnt/cephfs/lasair/system_status/status_<nid>.json`

Unit test is `tests/unit/common/src/test_manage_status.py`

This is where it is used:

- `pipeline/ingest/ingest.py` **add**
    - `today_alert`: Number of alerts seen by the ingest module today
    - `today_diaSource`: Number of diaSources put in Cassandra today

- `pipeline/filter/consume_alerts.py` **add**
    - `today_filter`: Number of alerts seen by the filter module today
    - `today_filter_out`: Number of alerts sent to the main database today

- `pipeline/filter/filter.py` **set**
    - `today_ztf`: Number of alerts that ZTF says have been issued today
    - `today_database`: Number of main database objects updated since midnight 
    - `total_count`: Number of objects in local filter database
    - `min_delay`: Hours since most recent alert

- `services/externalBrokers/TNS/poll_tns.py` **set**
    - `countTNS`: Number of records in TNS cache

- `utility/countAnnotations.py` **set**
    - `countAnnotations`: Number of annotations in Lasair
