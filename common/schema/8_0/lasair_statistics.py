schema = {
  "name": "lasair_statistics",
  "version": "1.0",
  "fields": [
    {
      "name": "nid",
      "type": "int",
      "doc": "Night number"
    },
    {
      "name": "name",
      "type": "string",
      "doc": "Which statistic"
    },
    {
      "name": "value",
      "type": "float",
      "doc": "The statistic being stored"
    }
  ],
  "indexes": [
    "PRIMARY KEY (nid, name)"
  ]
}
