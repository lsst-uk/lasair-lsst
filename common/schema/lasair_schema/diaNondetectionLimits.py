schema = {
  "name": "diaNondetectionLimits",
  "fields": [
    {
      "name": "ccdVisitId",
      "type": "long"
    },
    {
      "name": "midPointTai",
      "type": "double"
    },
    {
      "name": "filterName",
      "type": "string"
    },
    {
      "name": "diaNoise",
      "type": "float"
    },
    {
      "name": "diaObjectId",
      "type": "long"
    }
  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)"
  ]
}
