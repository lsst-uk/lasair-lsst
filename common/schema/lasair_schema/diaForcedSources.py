schema = {
  "name": "diaForcedSources",
  "fields": [
    {
      "name": "diaForcedSourceId",
      "type": "long"
    },
    {
      "name": "diaObjectId",
      "type": "long"
    },
    {
      "name": "ra",
      "type": "double"
    },
    {
      "name": "decl",
      "type": "double"
    },
    {
      "name": "visit",
      "type": "long"
    },
    {
      "name": "detector",
      "type": "int"
    },
    {
      "name": "psfFlux",
      "type": "float"
    },
    {
      "name": "psfFluxErr",
      "type": "float"
    },
    {
      "name": "midpointMjdTai",
      "type": "double"
    },
    {
      "name": "band",
      "type": "string"
    }
  ],
  "indexes": ['PRIMARY KEY ("diaObjectId","midpointMjdTai")']
}
