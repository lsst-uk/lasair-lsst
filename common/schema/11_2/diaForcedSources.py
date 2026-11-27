schema = {

  "indexes": [
    "PRIMARY KEY (\"diaObjectId\",\"midpointMjdTai\")"
  ],
  "name": "diaForcedSources",
  "fields": [
    {
      "name": "diaForcedSourceId",
      "type": "long",
      "doc": "Unique identifier of this DiaForcedSource."
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Id of the DiaObject that set the position for this forced measurement."
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
      "doc": "Forced PSF flux on the difference image at the DiaObject position. Positive if the source is brighter in the visit image than in the template."
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
      "doc": "Forced PSF flux on the visit image at the DiaObject position. Unlike psfFlux, it includes the flux of any static source and background."
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
      "doc": "Time when this record was marked invalid, expressed as Modified Julian Date, International Atomic Time. NULL unless the record has been withdrawn."
    }
  ]
}