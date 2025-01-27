CREATE TABLE IF NOT EXISTS cutouts(
"cutoutId" ascii,
"objectId" bigint,
"imjd" int,
"cutoutimage" blob,
PRIMARY KEY ("cutoutId", imjd)
)
WITH compaction=
{'class': 'org.apache.cassandra.db.compaction.TimeWindowCompactionStrategy', 
'compaction_window_size': '7', 
'compaction_window_unit': 'DAYS'}
AND default_time_to_live=7776000

