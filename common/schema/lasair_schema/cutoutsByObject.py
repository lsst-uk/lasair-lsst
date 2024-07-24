schema = {
  "name": "cutoutsbyObject",
  "fields": [
    {
      "name": "objectId",
      "type": "bigint"
    },
    {
      "name": "cutoutId",
      "type": "char"
    },
  ],
  "indexes": ["PRIMARY KEY (objectId, cutoutId)"]
}
