schema = {
  "name": "mma_area_hits",
  "version": "1.0",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "ZTF object identifier"
    },
    {
      "name": "mw_id",
      "type": "int",
      "doc": "MMA area identifier"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`diaObjectId`)"
  ]
}
