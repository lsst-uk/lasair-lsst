schema = {
  "name": "objects",
  "fields": [
    {
      "name": "htm16",
      "type": "long",
      "doc": "Hierarchical Triangular Mesh level 16",
      "extra": "NOT NULL"
    },

# These copied from the LSST diaObject
    { "name": "diaObjectId", "type": "long", "extra": "NOT NULL",
        "doc": "ID for this object" },
    { "name": "ra",       "type": "double", "doc": "Mean RA of this object" },
    { "name": "decl",     "type": "double", "doc": "Mean Dec of this object"},

    { "name": "g_psfFluxMean", "type": "float", 
        "doc": "Weighted mean point-source model magnitude for g filter" },
    { "name": "g_psfFluxMeanErr", "type": "float", 
        "doc": "Standard error of g_psfFluxMean" },

    { "name": "r_psfFluxMean", "type": "float", 
        "doc": "Weighted mean point-source model magnitude for r filter" },
    { "name": "r_psfFluxMeanErr", "type": "float", 
        "doc": "Standard error of r_psfFluxMean" },

# Counting, max, min
    { "name": "nSources",     "type": "int", 
        "extra": "NOT NULL",
        "doc": "Number of diaSources associated with this diaObject"},
    { "name": "nuSources", "type": "int", "doc": "Number of u sources" },
    { "name": "ngSources", "type": "int", "doc": "Number of u sources" },
    { "name": "nrSources", "type": "int", "doc": "Number of u sources" },
    { "name": "niSources", "type": "int", "doc": "Number of u sources" },
    { "name": "nzSources", "type": "int", "doc": "Number of u sources" },
    { "name": "nySources", "type": "int", "doc": "Number of u sources" },
    { "name": "maxTai", "type": "double", "doc": "Latest MJD of a diaSource" },
    { "name": "minTai", "type": "double", "doc": "Earliest MJD of a diaSource" },

# Latest Flux
    { "name": "uPSFlux", "type": "float", "doc": "Latest u flux" },
    { "name": "gPSFlux", "type": "float", "doc": "Latest g flux" },
    { "name": "rPSFlux", "type": "float", "doc": "Latest r flux" },
    { "name": "iPSFlux", "type": "float", "doc": "Latest i flux" },
    { "name": "zPSFlux", "type": "float", "doc": "Latest z flux" },
    { "name": "yPSFlux", "type": "float", "doc": "Latest y flux" },

# Sherlock
    { "name": "absFlux", "type": "float", 
        "doc":"Absolute flux if host galaxy with distance available"},

# Jump statistic
    { "name": "fluxJump", "type": "float", 
        "doc":"Number of sigma latest is above mean/sd of previous"},

# Exponential fitting
    { "name": "uExpRate", "type": "float", "doc": "Rate of increase of u" },
    { "name": "gExpRate", "type": "float", "doc": "Rate of increase of g" },
    { "name": "rExpRate", "type": "float", "doc": "Rate of increase of r" },
    { "name": "iExpRate", "type": "float", "doc": "Rate of increase of i" },
    { "name": "zExpRate", "type": "float", "doc": "Rate of increase of z" },
    { "name": "yExpRate", "type": "float", "doc": "Rate of increase of y" },
    { "name": "uExpRateErr", "type": "float", "doc": "Error of uExpRate" },
    { "name": "gExpRateErr", "type": "float", "doc": "Error of gExpRate" },
    { "name": "rExpRateErr", "type": "float", "doc": "Error of rExpRate" },
    { "name": "iExpRateErr", "type": "float", "doc": "Error of iExpRate" },
    { "name": "zExpRateErr", "type": "float", "doc": "Error of zExpRate" },
    { "name": "yExpRateErr", "type": "float", "doc": "Error of yExpRate" },

# Bazin-Exp-Blackbody
    { "name": "bazinExpRiseRate", "type": "float", 
        "doc": "Fitted Bazin or Exp rise rate" },
    { "name": "bazinExpFallRate", "type": "float", 
        "doc": "Fitted Bazin or Exp fall rate" },
    { "name": "bazinExpTemp", "type": "float", 
        "doc": "Fitted Bazin temperature, kiloKelvins" },
    { "name": "bazinExpRiseRateErr", "type": "float", 
        "doc": "Error of bazinExpRiseRate" },
    { "name": "bazinExpFallRateErr", "type": "float", 
        "doc": "Error of bazinExpFallRate" },
    { "name": "bazinExpTempErr", "type": "float", 
        "doc": "Error of bazinExpTemp"}


  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)",
    "KEY htmid16idx (htm16)",
    "KEY idxMaxTai (maxTai)"
  ]
}
