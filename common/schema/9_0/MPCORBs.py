schema = {
  'indexes':['PRIMARY KEY ("ssObjectId")'],
  "name": "MPCORBs",
  "fields": [
    {
      "name": "mpcDesignation",
      "type": "string",
      "doc": "Number or provisional designation (in packed form)."
    },
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "LSST unique identifier (if observed by LSST)."
    },
    {
      "name": "mpcH",
      "type": "float",
      "doc": "Absolute magnitude, H [mag]."
    },
    {
      "name": "epoch",
      "type": "double",
      "doc": "Epoch (in MJD, .0 TT) [d]."
    },
    {
      "name": "M",
      "type": "double",
      "doc": "Mean anomaly at the epoch [deg]."
    },
    {
      "name": "peri",
      "type": "double",
      "doc": "Argument of perihelion, J2000.0 [deg]."
    },
    {
      "name": "node",
      "type": "double",
      "doc": "Longitude of the ascending node, J2000.0 [deg]."
    },
    {
      "name": "incl",
      "type": "double",
      "doc": "Inclination to the ecliptic, J2000.0 [deg]."
    },
    {
      "name": "e",
      "type": "double",
      "doc": "Orbital eccentricity."
    },
    {
      "name": "a",
      "type": "double",
      "doc": "Semimajor axis [AU]."
    },
    {
      "name": "q",
      "type": "double",
      "doc": "Perihelion distance [AU]."
    },
    {
      "name": "t_p",
      "type": "double",
      "doc": "MJD of pericentric passage [d]."
    }
  ]
}