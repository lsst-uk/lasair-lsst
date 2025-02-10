schema = {
  'indexes':['PRIMARY KEY ("diaObjectId","midpointMjdTai")'],
  "name": "diaForcedSources",
  "fields": [
    {
      "doc": "Unique id.",
      "name": "diaForcedSourceId",
      "type": "long"
    },
    {
      "doc": "Id of the DiaObject that this DiaForcedSource was associated with.",
      "name": "diaObjectId",
      "type": "long"
    },
    {
      "doc": "Right ascension coordinate of the position of the DiaObject at time radecMjdTai.",
      "name": "ra",
      "type": "double"
    },
    {
      "doc": "Declination coordinate of the position of the DiaObject at time radecMjdTai.",
      "name": "decl",
      "type": "double"
    },
    {
      "doc": "Id of the visit where this forcedSource was measured.",
      "name": "visit",
      "type": "long"
    },
    {
      "doc": "Id of the detector where this forcedSource was measured. Datatype short instead of byte because of DB concerns about unsigned bytes.",
      "name": "detector",
      "type": "int"
    },
    {
      "doc": "Point Source model flux.",
      "name": "psfFlux",
      "type": "float"
    },
    {
      "doc": "Uncertainty of psfFlux.",
      "name": "psfFluxErr",
      "type": "float"
    },
    {
      "doc": "Effective mid-visit time for this diaForcedSource, expressed as Modified Julian Date, International Atomic Time.",
      "name": "midpointMjdTai",
      "type": "double"
    },
    {
      "doc": "Filter band this source was observed with.",
      "name": "band",
      "type": "string"
    }
  ]
}
