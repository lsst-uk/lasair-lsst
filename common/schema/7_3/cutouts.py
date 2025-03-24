schema = {
  "name": "cutouts",
  "fields": [
    {
      "name": "cutoutId",
      "type": "char"
    },
    {
      "name": "objectId",
      "type": "bigint"
    },
    {
      "name": "imjd",
      "type": "int"
    },
    {
      "name": "cutoutimage",
      "type": "blob"
    }
  ],
  "indexes": ['PRIMARY KEY ("cutoutId", imjd)'],
  "with": """WITH compaction=
{'class': 'org.apache.cassandra.db.compaction.TimeWindowCompactionStrategy', 
'compaction_window_size': '7', 
'compaction_window_unit': 'DAYS'}
AND default_time_to_live=7776000
"""
}
