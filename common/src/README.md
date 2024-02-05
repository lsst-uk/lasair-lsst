## The `manage_status` module

To store metrics about the progress of the ingestion pipeline.  Each set of metrics is distinguished by a `file_id`, so there can be many such sets.  In the current Lasair pipeline, this is generally the `nid` or night ID, so that a set of metrics is gathered for each night of alert ingestion. Below are the places it is used and the meaning of the keys that are used.  Some of the quantities are **set** by the code, and some are **add**. The former is a replacement value, the latter is an increment. 

Data files are in `/mnt/cephfs/lasair/system_status/status_<nid>.json`

Unit test is `tests/unit/common/src/test_manage_status.py`

The symbol * in the below means the node number: 0,1,2,3 for the ingest or filter cluster

This is where it is used:

- `pipeline/ingest/ingest.py` **add**
    - `today_alert`: Number of alerts seen by the ingest module today
    - `today_diaSource`: Number of diaSources put in Cassandra today
    - `icutout_*`: Time spend today storing cutouts in this node
    - `icassandra_*`: Time spend today storing Rubin data packets in this node
    - `ikafka_*`: Time spend today pushing kafka in this node
    - `itotal_*`: Total time spent today in this ingest node

- `pipeline/filter/consume_alerts.py` **add**
    - `today_filter`: Number of alerts seen by the filter module today
    - `today_filter_out`: Number of alerts sent to the main database today

- `pipeline/filter/filter.py` **set**
    - `today_ztf`: Number of alerts that ZTF says have been issued today
    - `today_database`: Number of main database objects updated since midnight 
    - `total_count`: Number of objects in local filter database
    - `min_delay`: Hours since most recent alert
    - `ffeatures_*`: Time spent today computing features in this node
    - `fwatchlist_*`: Time spent today computing watchlists in this node
    - `fwatchmap_*`: Time spent today computing watchmaps in this node
    - `ffilters_*`: Time spent today computing user filters in this node
    - `ftransfer_*`: Time spent today transferring to main database in this node
    - `ftotal_*`: Total time spent today in this filter node

- `services/externalBrokers/TNS/poll_tns.py` **set**
    - `countTNS`: Number of records in TNS cache

- `utility/countAnnotations.py` **set**
    - `countAnnotations`: Number of annotations in Lasair

Example output, 2 ingest nodes, 2 filter nodes, 2000 alerts each
```
{
    "nid": 2559,
    "update_time": "2024-01-04T12:16:08",
    "today_alert":      4000,
    "today_diaSource":  5106,
    "today_filter":     4000,
    "today_filter_out": 1424,
    "today_ztf":          -1,
    "today_database":  20622,
    "total_count":        -1,
    "min_delay":      "-1.0",

    "icutout_0":      0.0026,
    "icassandra_0": 110.26,
    "ikafka_0":      10.54,
    "itotal_0":      139.8,

    "icutout_1":       0.0019,
    "icassandra_1":   101.97,
    "ikafka_1":         7.446,
    "itotal_1":       121.2,

    "ffeatures_0":     19.40,
    "fwatchlist_0":     0.380,
    "fwatchmap_0":      0.052,
    "ffilters_0":       0.163,
    "ftransfer_0":      0.0800,
    "ftotal_0":        25.24,

    "ffeatures_1":     20.86,
    "fwatchlist_1":     0.369,
    "fwatchmap_1":      0.0082,
    "ffilters_1":       0.0112,
    "ftransfer_1":      0.0829,
    "ftotal_1":        26.56
}
```
