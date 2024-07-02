schema = {
  "name": "cutoutsbyObject",
  "fields": [
    {
      "name": "cutoutId",
      "type": "char"
    },
    {
      "name": "objectId",
      "type": "bigint"
    },
  ],
  "indexes": ["PRIMARY KEY (objectId)"]
}
