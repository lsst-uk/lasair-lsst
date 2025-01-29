schema = {
  'indexes':['PRIMARY KEY ("ssObjectId")'],
  "name": "ssObject",
  "fields": [
    {
      "doc": "Unique identifier.",
      "name": "ssObjectId",
      "type": "long"
    },
    {
      "doc": "The date the LSST first linked and submitted the discovery observations to the MPC. May be NULL if not an LSST discovery. The date format will follow general LSST conventions (MJD TAI, at the moment).",
      "name": "discoverySubmissionDate",
      "type": "double"
    },
    {
      "doc": "The time of the first LSST observation of this object (could be precovered) as Modified Julian Date, International Atomic Time.",
      "name": "firstObservationDate",
      "type": "double"
    },
    {
      "doc": "Arc of LSST observations.",
      "name": "arc",
      "type": "float"
    },
    {
      "doc": "Number of LSST observations of this object.",
      "name": "numObs",
      "type": "int"
    },
    {
      "doc": "Minimum orbit intersection distance to Earth.",
      "name": "MOID",
      "type": "float"
    },
    {
      "doc": "True anomaly of the MOID point.",
      "name": "MOIDTrueAnomaly",
      "type": "float"
    },
    {
      "doc": "Ecliptic longitude of the MOID point.",
      "name": "MOIDEclipticLongitude",
      "type": "float"
    },
    {
      "doc": "DeltaV at the MOID point.",
      "name": "MOIDDeltaV",
      "type": "float"
    },
    {
      "doc": "Best fit absolute magnitude (u band).",
      "name": "u_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (u band).",
      "name": "u_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (u band).",
      "name": "u_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (u band).",
      "name": "u_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (u band).",
      "name": "u_H_u_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (u band).",
      "name": "u_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (u band).",
      "name": "u_Ndata",
      "type": "int"
    },
    {
      "doc": "Best fit absolute magnitude (g band).",
      "name": "g_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (g band).",
      "name": "g_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (g band).",
      "name": "g_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (g band).",
      "name": "g_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (g band).",
      "name": "g_H_g_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (g band).",
      "name": "g_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (g band).",
      "name": "g_Ndata",
      "type": "int"
    },
    {
      "doc": "Best fit absolute magnitude (r band).",
      "name": "r_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (r band).",
      "name": "r_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (r band).",
      "name": "r_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (r band).",
      "name": "r_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (r band).",
      "name": "r_H_r_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (r band).",
      "name": "r_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (r band).",
      "name": "r_Ndata",
      "type": "int"
    },
    {
      "doc": "Best fit absolute magnitude (i band).",
      "name": "i_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (i band).",
      "name": "i_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (i band).",
      "name": "i_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (i band).",
      "name": "i_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (i band).",
      "name": "i_H_i_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (i band).",
      "name": "i_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (i band).",
      "name": "i_Ndata",
      "type": "int"
    },
    {
      "doc": "Best fit absolute magnitude (z band).",
      "name": "z_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (z band).",
      "name": "z_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (z band).",
      "name": "z_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (z band).",
      "name": "z_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (z band).",
      "name": "z_H_z_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (z band).",
      "name": "z_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (z band).",
      "name": "z_Ndata",
      "type": "int"
    },
    {
      "doc": "Best fit absolute magnitude (y band).",
      "name": "y_H",
      "type": "float"
    },
    {
      "doc": "Best fit G12 slope parameter (y band).",
      "name": "y_G12",
      "type": "float"
    },
    {
      "doc": "Uncertainty of H (y band).",
      "name": "y_HErr",
      "type": "float"
    },
    {
      "doc": "Uncertainty of G12 (y band).",
      "name": "y_G12Err",
      "type": "float"
    },
    {
      "doc": "H-G12 covariance (y band).",
      "name": "y_H_y_G12_Cov",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the phase curve fit (y band).",
      "name": "y_Chi2",
      "type": "float"
    },
    {
      "doc": "The number of data points used to fit the phase curve (y band).",
      "name": "y_Ndata",
      "type": "int"
    },
    {
      "doc": "median `extendedness` value from the DIASource.",
      "name": "medianExtendedness",
      "type": "float"
    }
  ]
}