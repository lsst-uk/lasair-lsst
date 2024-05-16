schema = {
  "name": "DiaSources",
  "fields": [
    {
      "name": "diaSourceId",
      "type": "long",
      "doc": "Unique id."
    },
    {
      "name": "ccdVisitId",
      "type": "long",
      "doc": "Id of the ccdVisit where this diaSource was measured. Note that we are allowing a diaSource to belong to multiple amplifiers, but it may not span multiple ccds."
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Id of the diaObject this source was associated with, if any. If not, it is set to NULL (each diaSource will be associated with either a diaObject or ssObject)."
    },
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "Id of the ssObject this source was associated with, if any. If not, it is set to NULL (each diaSource will be associated with either a diaObject or ssObject)."
    },
    {
      "name": "nameTrue",
      "type": "string",
      "doc": "MPC or simulation designation of the moving object"
    },
    {
      "name": "ssObjectReassocTime",
      "type": "timestamp",
      "doc": "Time when this diaSource was reassociated from diaObject to ssObject (if such reassociation happens, otherwise NULL)."
    },
    {
      "name": "midPointMjdTai",
      "type": "double",
      "doc": "Effective mid-exposure time for this diaSource."
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "RA-coordinate of the center of this diaSource."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Dec-coordinate of the center of this diaSource."
    },
    {
      "name": "decErr",
      "type": "float",
      "doc": "Uncertainty of dec."
    },
    {
      "name": "ra_dec_Cov",
      "type": "float",
      "doc": "Covariance between ra and dec."
    },
    {
      "name": "snr",
      "type": "float",
      "doc": "The signal-to-noise ratio at which this source was detected in the difference image."
    },
    {
      "name": "band",
      "type": "string",
      "doc": "Name of the band used to take the exposure where this source was measured"
    },
    {
      "name": "mag",
      "type": "float",
      "doc": "Magnitude. This is a placeholder and should be replaced by flux."
    },
    {
      "name": "magErr",
      "type": "float",
      "doc": "Magnitude error. This is a placeholder and should be replaced by flux error."
    },
    {
      "name": "magTrueVband",
      "type": "float",
      "doc": "True (noiseless) V-band magnitude of the simulated diaSource"
    },
    {
      "name": "raTrue",
      "type": "double",
      "doc": "True (noiseless) right ascension of the simulated diaSource"
    },
    {
      "name": "decTrue",
      "type": "double",
      "doc": "True (noiseless) declination of the simulated diaSource"
    }
  ],
  "indexes": ["PRIMARY KEY (ssObjectId, midPointMjdTai)"]
}
