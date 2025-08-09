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
      "name": "observation_reason",
      "type": "string",
      "origin": "lsst",
      "doc": "Latest observation reason for this object"
    },
    {
      "name": "target_name",
      "type": "string",
      "origin": "lsst",
      "doc": "Latest target name for this object"
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
      "name": "pmRa",
      "type": "float",
      "origin": "lsst",
      "doc": "Proper motion in right ascension (mas/yr)"
    },
    {
      "name": "pmDec",
      "type": "float",
      "origin": "lsst",
      "doc": "Proper motion in declination (mas/yr)"
    },
    {
      "section": "Lightcurve interval",
      "doc": "MJD of the first and last diaSource of this diaObject"
    },
    {
      "name": "lastDiaSourceMjdTai",
      "type": "double",
      "origin": "lasair",
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
      "doc": "Weighted mean point-source model magnitude for u filter. (nJy)"
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
      "doc": "Weighted mean point-source model magnitude for g filter. (nJy)"
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
      "doc": "Weighted mean point-source model magnitude for r filter. (nJy)"
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
      "doc": "Weighted mean point-source model magnitude for i filter. (nJy)"
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
      "doc": "Weighted mean point-source model magnitude for z filter. (nJy)"
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
      "doc": "Weighted mean point-source model magnitude for y filter. (nJy)"
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float",
      "origin": "lsst",
      "doc": "Standard error of y_psfFluxMean. (nJy)"
    },
    {
      "section": "Counting",
      "doc": "Counts of diaSources of different bands"
    },
    {
      "name": "nSources",
      "type": "int",
      "origin": "lasair",
      "doc": "Number of diaSources associated with this diaObject",
      "extra": "NOT NULL"
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
      "name": "nearbyObj1",
      "type": "long",
      "origin": "lsst",
      "doc": "Id of the closest nearby object."
    },
    {
      "name": "nearbyObj1Dist",
      "type": "float",
      "origin": "lsst",
      "doc": "Distance to nearbyObj1 (arcsec)"
    },
    {
      "name": "nearbyObj1LnP",
      "type": "float",
      "origin": "lsst",
      "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj1."
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
      "doc": "If Bazin fit, the peak flux (nJy)"
    },
    {
      "name": "BBBPeakMJD",
      "type": "float",
      "origin": "lasair",
      "doc": "If Bazin fit, the time of the peak brightness"
    },
    {
      "name": "BBBPeakAbsMag",
      "type": "float",
      "origin": "lasair",
      "doc": "If Bazin fit and Sherlock host with distance, the peak absolute magnitude"
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
      "name": "validityStart",
      "type": "long",
      "doc": "Processing time when validity of this diaObject starts."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra."
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
      "name": "u_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of u_psfFlux."
    },
    {
      "name": "u_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of u_psfFlux around u_psfFluxMean."
    },
    {
      "name": "u_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute u_psfFluxChi2."
    },
    {
      "name": "u_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for u filter."
    },
    {
      "name": "u_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_fpFluxMean."
    },
    {
      "name": "g_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of g_psfFlux."
    },
    {
      "name": "g_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of g_psfFlux around g_psfFluxMean."
    },
    {
      "name": "g_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute g_psfFluxChi2."
    },
    {
      "name": "g_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for g filter."
    },
    {
      "name": "g_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_fpFluxMean."
    },
    {
      "name": "r_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of r_psfFlux."
    },
    {
      "name": "r_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of r_psfFlux around r_psfFluxMean."
    },
    {
      "name": "r_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute r_psfFluxChi2."
    },
    {
      "name": "r_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for r filter."
    },
    {
      "name": "r_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_fpFluxMean."
    },
    {
      "name": "i_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of i_psfFlux."
    },
    {
      "name": "i_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of i_psfFlux around i_psfFluxMean."
    },
    {
      "name": "i_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute i_psfFluxChi2."
    },
    {
      "name": "i_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for i filter."
    },
    {
      "name": "i_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_fpFluxMean."
    },
    {
      "name": "z_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of z_psfFlux."
    },
    {
      "name": "z_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of z_psfFlux around z_psfFluxMean."
    },
    {
      "name": "z_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute z_psfFluxChi2."
    },
    {
      "name": "z_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for z filter."
    },
    {
      "name": "z_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_fpFluxMean."
    },
    {
      "name": "y_psfFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of y_psfFlux."
    },
    {
      "name": "y_psfFluxChi2",
      "type": "float",
      "doc": "Chi^2 statistic for the scatter of y_psfFlux around y_psfFluxMean."
    },
    {
      "name": "y_psfFluxNdata",
      "type": "int",
      "doc": "The number of data points used to compute y_psfFluxChi2."
    },
    {
      "name": "y_fpFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for y filter."
    },
    {
      "name": "y_fpFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_fpFluxMean."
    },
    {
      "name": "u_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for u filter."
    },
    {
      "name": "u_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_scienceFluxMean."
    },
    {
      "name": "u_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of u_scienceFlux."
    },
    {
      "name": "g_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for g filter."
    },
    {
      "name": "g_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_scienceFluxMean."
    },
    {
      "name": "g_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of g_scienceFlux."
    },
    {
      "name": "r_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for r filter."
    },
    {
      "name": "r_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_scienceFluxMean."
    },
    {
      "name": "r_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of r_scienceFlux."
    },
    {
      "name": "i_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for i filter."
    },
    {
      "name": "i_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_scienceFluxMean."
    },
    {
      "name": "i_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of i_scienceFlux."
    },
    {
      "name": "z_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for z filter."
    },
    {
      "name": "z_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_scienceFluxMean."
    },
    {
      "name": "z_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of z_scienceFlux."
    },
    {
      "name": "y_scienceFluxMean",
      "type": "float",
      "doc": "Weighted mean forced photometry flux for y filter."
    },
    {
      "name": "y_scienceFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_scienceFluxMean."
    },
    {
      "name": "y_scienceFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of y_scienceFlux."
    },
    {
      "name": "u_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the u band fluxes."
    },
    {
      "name": "u_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed u band fluxes."
    },
    {
      "name": "u_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed u band fluxes."
    },
    {
      "name": "u_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between u band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "u_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the u band flux errors."
    },
    {
      "name": "g_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the g band fluxes."
    },
    {
      "name": "g_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed g band fluxes."
    },
    {
      "name": "g_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed g band fluxes."
    },
    {
      "name": "g_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between g band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "g_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the g band flux errors."
    },
    {
      "name": "r_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the r band fluxes."
    },
    {
      "name": "r_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed r band fluxes."
    },
    {
      "name": "r_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed r band fluxes."
    },
    {
      "name": "r_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between r band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "r_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the r band flux errors."
    },
    {
      "name": "i_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the i band fluxes."
    },
    {
      "name": "i_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed i band fluxes."
    },
    {
      "name": "i_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed i band fluxes."
    },
    {
      "name": "i_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between i band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "i_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the i band flux errors."
    },
    {
      "name": "z_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the z band fluxes."
    },
    {
      "name": "z_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed z band fluxes."
    },
    {
      "name": "z_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed z band fluxes."
    },
    {
      "name": "z_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between z band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "z_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the z band flux errors."
    },
    {
      "name": "y_psfFluxSkew",
      "type": "float",
      "doc": "Skewness of the y band fluxes."
    },
    {
      "name": "y_psfFluxMin",
      "type": "float",
      "doc": "Minimum observed y band fluxes."
    },
    {
      "name": "y_psfFluxMax",
      "type": "float",
      "doc": "Maximum observed y band fluxes."
    },
    {
      "name": "y_psfFluxMaxSlope",
      "type": "float",
      "doc": "Maximum slope between y band flux obsevations max(delta_flux/delta_time)."
    },
    {
      "name": "y_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the y band flux errors."
    },
    {
      "name": "lastNonForcedSource",
      "type": "long",
      "doc": "Last time when non-forced DIASource was seen for this object."
    },
    {
      "name": "nDiaSources",
      "type": "int",
      "doc": "Total number of DiaSources associated with this DiaObject."
    }
  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)",
    "KEY htmid16idx (htm16)",
    "KEY idxMaxTai (lastDiaSourceMJD)"
  ]
}