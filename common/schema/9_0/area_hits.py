schema = {
  "name": "area_hits",
  "version": "1.0",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "LSST object identifier"
    },
    {
      "name": "ar_id",
      "type": "int",
      "doc": "Area identifier"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`diaObjectId`)"
  ]
}
