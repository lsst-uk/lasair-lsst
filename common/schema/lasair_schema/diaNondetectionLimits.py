schema = {
  "name": "diaNondetectionLimits",
  "fields": [
    {
      "name": "ccdVisitId",
      "type": "long"
    },
    {
      "name": "midpointMjdTai",
      "type": "double"
    },
    {
      "name": "band",
      "type": "string"
    },
    {
      "name": "diaNoise",
      "type": "float"
    }
  ],
  "indexes": ['PRIMARY KEY ("midpointMjdTai")']
}
