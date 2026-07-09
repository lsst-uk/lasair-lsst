schema = {
  "name": "cutoutsbyObject",
  "fields": [
    {
      "name": "objectId",
      "type": "bigint"
    },
        {
      "name": "isDiaObject",
      "type": "boolean"
    },
    {
      "name": "cutoutId",
      "type": "char"
    },
  ],
  "indexes": ['PRIMARY KEY ("objectId", "cutoutId")']
}
