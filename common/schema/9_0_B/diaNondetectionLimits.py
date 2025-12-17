schema = {
  'indexes':['PRIMARY KEY ("midpointMjdTai")'],
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
      "doc": "Right ascension coordinate of the position of the DiaObject [deg]."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Declination coordinate of the position of the DiaObject [deg]."
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
      "doc": "Point Source model flux [nJy]."
    },
    {
      "name": "psfFluxErr",
      "type": "float",
      "doc": "Uncertainty of psfFlux [nJy]."
    },
    {
      "name": "midpointMjdTai",
      "type": "double",
      "doc": "Effective mid-visit time for this diaForcedSource, expressed as Modified Julian Date, International Atomic Time [d]."
    },
    {
      "name": "scienceFlux",
      "type": "float",
      "doc": "Forced photometry flux for a point source model measured on the visit image centered at the DiaObject position [nJy]."
    },
    {
      "name": "scienceFluxErr",
      "type": "float",
      "doc": "Uncertainty of scienceFlux [nJy]."
    },
    {
      "name": "band",
      "type": "string",
      "doc": "Filter band this source was observed with."
    },
    {
      "name": "timeProcessedMjdTai",
      "type": "double",
      "doc": "Time when this record was generated, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "timeWithdrawnMjdTai",
      "type": "double",
      "doc": "Time when this record was marked invalid, expressed as Modified Julian Date, International Atomic Time."
    }
  ]
}