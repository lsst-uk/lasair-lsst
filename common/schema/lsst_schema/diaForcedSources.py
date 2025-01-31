schema = {
  'indexes':['PRIMARY KEY ("diaObjectId","midpointMjdTai")'],
  "name": "diaForcedSources",
  "fields": [
    {
      "name": "diaForcedSourceId",
      "type": "long",
      "doc": "Unique id."
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Id of the DiaObject that this DiaForcedSource was associated with."
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "Right ascension coordinate of the position of the DiaObject at time radecMjdTai."
    },
    {
      "name": "dec",
      "type": "double",
      "doc": "Declination coordinate of the position of the DiaObject at time radecMjdTai."
    },
    {
      "name": "visit",
      "type": "long",
      "doc": "Id of the visit where this forcedSource was measured."
    },
    {
      "name": "detector",
      "type": "int",
      "doc": "Id of the detector where this forcedSource was measured. Datatype short instead of byte because of DB concerns about unsigned bytes."
    },
    {
      "name": "psfFlux",
      "type": "float",
      "doc": "Point Source model flux."
    },
    {
      "name": "psfFluxErr",
      "type": "float",
      "doc": "Uncertainty of psfFlux."
    },
    {
      "name": "midpointMjdTai",
      "type": "double",
      "doc": "Effective mid-visit time for this diaForcedSource, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "band",
      "type": "string",
      "doc": "Filter band this source was observed with."
    }
  ]
}