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
  "indexes": ['PRIMARY KEY (("imjd", "cutoutId"))']
}
