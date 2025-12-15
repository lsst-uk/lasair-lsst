schema = {
  "name": "objects",
  "fields": [
    {
      "section": "Basic information",
      "doc": "ID, position, proper motion"
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "origin": "lsst",
      "doc": "ID for this object",
      "extra": "NOT NULL"
    },
    {
      "name": "ra",
      "type": "double",
      "origin": "lsst",
      "doc": "Mean RA of this object"
    },
    {
      "name": "decl",
      "type": "double",
      "origin": "lsst",
      "doc": "Mean Dec of this object"
    },
    {
      "section": "Lightcurve interval",
      "doc": "MJD of the first and last diaSource of this diaObject"
    },
    {
      "name": "lastDiaSourceMjdTai",
      "type": "double",
      "origin": "lsst",
      "doc": "Latest MJD of a diaSource"
    },
    {
      "name": "firstDiaSourceMjdTai",
      "type": "double",
      "origin": "lsst",
      "doc": "Earliest MJD of a diaSource"
    },
    {
      "section": "Latest Flux",
      "doc": "Most recent fluxes with errors"
    },
    {
      "name": "latest_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest flux of any band (nJy)"
    },
    {
      "name": "u_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest u flux (nJy)"
    },
    {
      "name": "u_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest u flux"
    },
    {
      "name": "u_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for u filter. (nJy)"
    },
    {
      "name": "u_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of u_psfFluxMean. (nJy)"
    },
    {
      "name": "g_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest g flux (nJy)"
    },
    {
      "name": "g_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest g flux"
    },
    {
      "name": "g_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for g filter. (nJy)"
    },
    {
      "name": "g_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of g_psfFluxMean. (nJy)"
    },
    {
      "name": "r_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest r flux (nJy)"
    },
    {
      "name": "r_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest r flux"
    },
    {
      "name": "r_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for r filter. (nJy)"
    },
    {
      "name": "r_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of r_psfFluxMean. (nJy)"
    },
    {
      "name": "i_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest i flux (nJy)"
    },
    {
      "name": "i_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest i flux"
    },
    {
      "name": "i_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for i filter. (nJy)"
    },
    {
      "name": "i_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of i_psfFluxMean. (nJy)"
    },
    {
      "name": "z_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest z flux (nJy)"
    },
    {
      "name": "z_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest z flux"
    },
    {
      "name": "z_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for z filter. (nJy)"
    },
    {
      "name": "z_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of z_psfFluxMean. (nJy)"
    },
    {
      "name": "y_psfFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest y flux (nJy)"
    },
    {
      "name": "y_latestMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "MJD of Latest y flux"
    },
    {
      "name": "y_psfFluxMean",
      "type": "float",
      "origin": "lsst",
      "doc": "Weighted mean point-source model flux for y filter. (nJy)"
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of y_psfFluxMean. (nJy)"
    },
    {
      "section": "Counting and Reliability",
      "doc": "Counts of diaSources, median of R"
    },
    {
      "name": "medianR",
      "type": "float",
      "origin": "lasair",
      "doc": "Median of reliability for the diaSources in this diaObject"
    },
    {
      "name": "latestR",
      "type": "float",
      "origin": "lasair",
      "doc": "Most recent reliability for the diaSources in this diaObject"
    },
    {
      "name": "nDiaSources",
      "type": "int",
      "origin": "lsst",
      "doc": "Number of diaSources associated with this diaObject"
    },
    {
      "name": "nSourcesGood",
      "type": "int",
      "origin": "lasair",
      "doc": "Number sources with reliability > 0.5"
    },
    {
      "name": "nuSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of u sources"
    },
    {
      "name": "ngSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of g sources"
    },
    {
      "name": "nrSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of r sources"
    },
    {
      "name": "niSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of i sources"
    },
    {
      "name": "nzSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of z sources"
    },
    {
      "name": "nySources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of y sources"
    },
    {
      "section": "Other/Nearest objects",
      "doc": "Other/Nearest objects from LSST and other catalogs"
    },
    {
      "name": "tns_name",
      "type": "string",
      "origin": "external",
      "doc": "TNS name of this object if it exists"
    },
    {
      "section": "Absolute magnitude",
      "doc": "Brightness at 1 parsec"
    },
    {
      "name": "absMag",
      "type": "float",
      "origin": "lasair",
      "doc": "Peak absolute magnitude (extinction corrected) if host galaxy with distance available"
    },
    {
      "name": "absMagMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "Peak absolute magnitude time if host galaxy with distance available"
    },
    {
      "section": "BazinBlackBody (BBB)",
      "doc": "Lightcurve fit as Bazin or Exp in time, Blackbody in wavelength"
    },
    {
      "name": "BBBRiseRate",
      "type": "float",
      "origin": "lasair",
      "doc": "Fitted Bazin or Exp rise rate"
    },
    {
      "name": "BBBFallRate",
      "type": "float",
      "origin": "lasair",
      "doc": "Fitted Bazin fall rate or NULL if Exp"
    },
    {
      "name": "BBBTemp",
      "type": "float",
      "origin": "lasair",
      "doc": "Fitted Bazin temperature, (kiloKelvins)"
    },
    {
      "name": "BBBPeakFlux",
      "type": "float",
      "origin": "lasair",
      "doc": "If Bazin fit, the peak flux (nJy), else NULL"
    },
    {
      "name": "BBBPeakMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "If Bazin fit, the time of the peak brightness, else NULL"
    },
    {
      "name": "BBBPeakAbsMag",
      "type": "float",
      "origin": "lasair",
      "doc": "If Bazin fit and Sherlock host with distance, the peak absolute magnitude, else NULL"
    },
    {
      "section": "Milky Way",
      "doc": "Galactic latitude and extinction"
    },
    {
      "name": "glat",
      "type": "float",
      "origin": "lasair",
      "doc": "Galactic latitude"
    },
    {
      "name": "ebv",
      "type": "float",
      "origin": "lasair",
      "doc": "Extinction E(B-V) Schlegel, Finkbeiner & Davis (1998)"
    },
    {
      "section": "Jump detector",
      "doc": "Number of sigma jump from 20 day mean"
    },
    {
      "name": "jump1",
      "type": "float",
      "origin": "lasair",
      "doc": "Largest sigma jump of recent flux from previous -70 to -10  days"
    },
    {
      "name": "jump2",
      "type": "float",
      "origin": "lasair",
      "doc": "Largest sigma jump of recent flux in different band from previous -70 to -10  days"
    },
    {
      "section": "Pair colours",
      "doc": "Colours from 33-minute paired diaSources"
    },
    {
      "name": "latestPairMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "Latest pair MJD"
    },
    {
      "name": "latestPairColourMag",
      "type": "float",
      "origin": "lasair",
      "doc": "Magnitude difference from latest pair"
    },
    {
      "name": "latestPairColourBands",
      "type": "string",
      "origin": "lasair",
      "doc": "Bands used for latest pair colour, eg g-r, u-r"
    },
    {
      "name": "latestPairColourTemp",
      "type": "float",
      "origin": "lasair",
      "doc": "Extinction corrected effective temperature from latest pair, kiloKelvin"
    },
    {
      "name": "penultimatePairMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "Penultimate pair MJD"
    },
    {
      "name": "penultimatePairColourMag",
      "type": "float",
      "origin": "lasair",
      "doc": "Magnitude difference from Penultimate pair"
    },
    {
      "name": "penultimatePairColourBands",
      "type": "string",
      "origin": "lasair",
      "doc": "Bands used for penultimate pair colour, eg g-r, u-r"
    },
    {
      "name": "penultimatePairColourTemp",
      "type": "float",
      "origin": "lasair",
      "doc": "Extinction corrected effective temperature from penultimate pair, kiloKelvin"
    },
    {
      "section": "Utility",
      "doc": "Other attributes"
    },
    {
      "name": "htm16",
      "type": "long",
      "origin": "lasair",
      "doc": "Hierarchical Triangular Mesh level 16",
      "extra": "NOT NULL"
    },
    {
      "name": "timestamp",
      "type": "timestamp",
      "extra": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
      "origin": "external",
      "doc": "Time at which this object last modified"
    }
  ],
  "ext_fields": [
    {
      "name": "validityStartMjdTai",
      "type": "double",
      "doc": "Processing time when validity of this diaObject starts, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra [deg]."
    },
    {
      "name": "decErr",
      "type": "float",
      "doc": "Uncertainty of dec [deg]."
    },
    {
      "name": "ra_dec_Cov",
      "type": "float",
      "doc": "Covariance between ra and dec [deg**2]."
    },
    {
      "name": "u_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of u_psfFlux [nJy]."
    },
    {
      "name": "u_psfFluxNdata",
      "type": "int",
      "doc": "The number of u-band data points."
    },
    {
      "name": "u_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for u filter [nJy]."
    },
    {
      "name": "u_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_fpFluxMean [nJy]."
    },
    {
      "name": "g_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of g_psfFlux [nJy]."
    },
    {
      "name": "g_psfFluxNdata",
      "type": "int",
      "doc": "The number of g-band data points."
    },
    {
      "name": "g_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for g filter [nJy]."
    },
    {
      "name": "g_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_fpFluxMean [nJy]."
    },
    {
      "name": "r_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of r_psfFlux [nJy]."
    },
    {
      "name": "r_psfFluxNdata",
      "type": "int",
      "doc": "The number of r-band data points."
    },
    {
      "name": "r_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for r filter [nJy]."
    },
    {
      "name": "r_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_fpFluxMean [nJy]."
    },
    {
      "name": "i_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of i_psfFlux [nJy]."
    },
    {
      "name": "i_psfFluxNdata",
      "type": "int",
      "doc": "The number of i-band data points."
    },
    {
      "name": "i_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for i filter [nJy]."
    },
    {
      "name": "i_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_fpFluxMean [nJy]."
    },
    {
      "name": "z_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of z_psfFlux [nJy]."
    },
    {
      "name": "z_psfFluxNdata",
      "type": "int",
      "doc": "The number of z-band data points."
    },
    {
      "name": "z_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for z filter [nJy]."
    },
    {
      "name": "z_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_fpFluxMean [nJy]."
    },
    {
      "name": "y_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of y_psfFlux [nJy]."
    },
    {
      "name": "y_psfFluxNdata",
      "type": "int",
      "doc": "The number of y-band data points."
    },
    {
      "name": "y_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for y filter [nJy]."
    },
    {
      "name": "y_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_fpFluxMean [nJy]."
    },
    {
      "name": "u_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for u filter [nJy]."
    },
    {
      "name": "u_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_scienceFluxMean [nJy]."
    },
    {
      "name": "g_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for g filter [nJy]."
    },
    {
      "name": "g_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_scienceFluxMean [nJy]."
    },
    {
      "name": "r_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for r filter [nJy]."
    },
    {
      "name": "r_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_scienceFluxMean [nJy]."
    },
    {
      "name": "i_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for i filter [nJy]."
    },
    {
      "name": "i_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_scienceFluxMean [nJy]."
    },
    {
      "name": "z_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for z filter [nJy]."
    },
    {
      "name": "z_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_scienceFluxMean [nJy]."
    },
    {
      "name": "y_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for y filter [nJy]."
    },
    {
      "name": "y_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_scienceFluxMean [nJy]."
    },
    {
      "name": "u_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed u band fluxes [nJy]."
    },
    {
      "name": "u_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed u band fluxes [nJy]."
    },
    {
      "name": "u_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between u band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "u_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the u band flux errors [nJy]."
    },
    {
      "name": "g_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed g band fluxes [nJy]."
    },
    {
      "name": "g_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed g band fluxes [nJy]."
    },
    {
      "name": "g_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between g band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "g_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the g band flux errors [nJy]."
    },
    {
      "name": "r_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed r band fluxes [nJy]."
    },
    {
      "name": "r_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed r band fluxes [nJy]."
    },
    {
      "name": "r_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between r band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "r_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the r band flux errors [nJy]."
    },
    {
      "name": "i_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed i band fluxes [nJy]."
    },
    {
      "name": "i_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed i band fluxes [nJy]."
    },
    {
      "name": "i_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between i band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "i_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the i band flux errors [nJy]."
    },
    {
      "name": "z_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed z band fluxes [nJy]."
    },
    {
      "name": "z_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed z band fluxes [nJy]."
    },
    {
      "name": "z_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between z band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "z_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the z band flux errors [nJy]."
    },
    {
      "name": "y_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed y band fluxes [nJy]."
    },
    {
      "name": "y_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed y band fluxes [nJy]."
    },
    {
      "name": "y_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between y band flux obsevations max(delta_flux/delta_time) [nJy/d]."
    },
    {
      "name": "y_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the y band flux errors [nJy]."
    }
  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)",
    "KEY htmid16idx (htm16)",
    "KEY idxMaxTai (lastDiaSourceMjdTai)"
  ]
}