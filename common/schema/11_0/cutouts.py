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
      "name": "isDiaObject",
      "type": "boolean"
    },
    {
      "name": "cutoutimage",
      "type": "blob"
    }
  ],
  "indexes": ['PRIMARY KEY ("cutoutId")'],
  "with": """WITH compaction=
{'class': 'org.apache.cassandra.db.compaction.TimeWindowCompactionStrategy', 
'compaction_window_size': '7', 
'compaction_window_unit': 'DAYS'}
AND default_time_to_live=31536000
"""
}
