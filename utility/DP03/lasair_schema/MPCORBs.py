schema = {
  "name": "MPCORBs",
  "fields": [
    {
      "name": "mpcDesignation",
      "type": "string",
      "doc": "MPCORB: Number or provisional designation (in packed form)"
    },
    {
      "name": "mpcNumber",
      "type": "int",
      "doc": "MPC number (if the asteroid has been numbered; NULL otherwise). Provided for convenience."
    },
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "LSST unique identifier (if observed by LSST)"
    },
    {
      "name": "mpcH",
      "type": "float",
      "doc": "MPCORB: Absolute magnitude, H"
    },
    {
      "name": "mpcG",
      "type": "float",
      "doc": "MPCORB: Slope parameter, G"
    },
    {
      "name": "epoch",
      "type": "double",
      "doc": "MPCORB: Epoch (in MJD, .0 TT)"
    },
    {
      "name": "tperi",
      "type": "double",
      "doc": "MPCORB: MJD of pericentric passage"
    },
    {
      "name": "peri",
      "type": "double",
      "doc": "MPCORB: Argument of perihelion, J2000.0 (degrees)"
    },
    {
      "name": "node",
      "type": "double",
      "doc": "MPCORB: Longitude of the ascending node, J2000.0 (degrees)"
    },
    {
      "name": "incl",
      "type": "double",
      "doc": "MPCORB: Inclination to the ecliptic, J2000.0 (degrees)"
    },
    {
      "name": "e",
      "type": "double",
      "doc": "MPCORB: Orbital eccentricity"
    },
    {
      "name": "n",
      "type": "double",
      "doc": "MPCORB: Mean daily motion (degrees per day)"
    },
    {
      "name": "q",
      "type": "double",
      "doc": "MPCORB: Perihelion distance (AU)"
    },
    {
      "name": "uncertaintyParameter",
      "type": "string",
      "doc": "MPCORB: Uncertainty parameter, U"
    },
    {
      "name": "reference",
      "type": "string",
      "doc": "MPCORB: Reference"
    },
    {
      "name": "nobs",
      "type": "int",
      "doc": "MPCORB: Number of observations"
    },
    {
      "name": "nopp",
      "type": "int",
      "doc": "MPCORB: Number of oppositions"
    },
    {
      "name": "arc",
      "type": "float",
      "doc": "MPCORB: Arc (days), for single-opposition objects"
    },
    {
      "name": "arcStart",
      "type": "timestamp",
      "doc": "MPCORB: Year of first observation (for multi-opposition objects)"
    },
    {
      "name": "arcEnd",
      "type": "timestamp",
      "doc": "MPCORB: Year of last observation (for multi-opposition objects)"
    },
    {
      "name": "rms",
      "type": "float",
      "doc": "MPCORB: r.m.s residual (\")"
    },
    {
      "name": "pertsShort",
      "type": "string",
      "doc": "MPCORB: Coarse indicator of perturbers (blank if unperturbed one-opposition object)"
    },
    {
      "name": "pertsLong",
      "type": "string",
      "doc": "MPCORB: Precise indicator of perturbers (blank if unperturbed one-opposition object)"
    },
    {
      "name": "computer",
      "type": "string",
      "doc": "MPCORB: Computer name"
    },
    {
      "name": "flags",
      "type": "int",
      "doc": "MPCORB: 4-hexdigit flags. See https://minorplanetcenter.net//iau/info/MPOrbitFormat.html for details"
    },
    {
      "name": "fullDesignation",
      "type": "string",
      "doc": "MPCORB: Readable designation"
    },
    {
      "name": "lastIncludedObservation",
      "type": "float",
      "doc": "MPCORB: Date of last observation included in orbit solution"
    }
  ],
  "indexes": ["PRIMARY KEY (ssObjectId)"]
}
