schema = {
  'indexes':['PRIMARY KEY ("diaObjectId", "midpointMjdTai", "diaSourceId")'],
  "name": "diaSource",
  "fields": [
    {
      "doc": "Unique identifier of this DiaSource.",
      "name": "diaSourceId",
      "type": "long"
    },
    {
      "doc": "Id of the visit where this diaSource was measured.",
      "name": "visit",
      "type": "long"
    },
    {
      "doc": "Id of the detector where this diaSource was measured. Datatype short instead of byte because of DB concerns about unsigned bytes.",
      "name": "detector",
      "type": "int"
    },
    {
      "doc": "Id of the diaObject this source was associated with, if any. If not, it is set to NULL (each diaSource will be associated with either a diaObject or ssObject).",
      "name": "diaObjectId",
      "type": "long"
    },
    {
      "doc": "Id of the ssObject this source was associated with, if any. If not, it is set to NULL (each diaSource will be associated with either a diaObject or ssObject).",
      "name": "ssObjectId",
      "type": "long"
    },
    {
      "doc": "Id of the parent diaSource this diaSource has been deblended from, if any.",
      "name": "parentDiaSourceId",
      "type": "long"
    },
    {
      "doc": "Effective mid-visit time for this diaSource, expressed as Modified Julian Date, International Atomic Time.",
      "name": "midpointMjdTai",
      "type": "double"
    },
    {
      "doc": "Right ascension coordinate of the center of this diaSource.",
      "name": "ra",
      "type": "double"
    },
    {
      "doc": "Uncertainty of ra.",
      "name": "raErr",
      "type": "float"
    },
    {
      "doc": "Declination coordinate of the center of this diaSource.",
      "name": "decl",
      "type": "double"
    },
    {
      "doc": "Uncertainty of dec.",
      "name": "decErr",
      "type": "float"
    },
    {
      "doc": "Covariance between ra and dec.",
      "name": "ra_dec_Cov",
      "type": "float"
    },
    {
      "doc": "x position computed by a centroiding algorithm.",
      "name": "x",
      "type": "float"
    },
    {
      "doc": "Uncertainty of x.",
      "name": "xErr",
      "type": "float"
    },
    {
      "doc": "y position computed by a centroiding algorithm.",
      "name": "y",
      "type": "float"
    },
    {
      "doc": "Uncertainty of y.",
      "name": "yErr",
      "type": "float"
    },
    {
      "doc": "Covariance between x and y.",
      "name": "x_y_Cov",
      "type": "float"
    },
    {
      "doc": "General centroid algorithm failure flag; set if anything went wrong when fitting the centroid. Another centroid flag field should also be set to provide more information.",
      "name": "centroid_flag",
      "type": "boolean"
    },
    {
      "doc": "Source was detected as significantly negative.",
      "name": "is_negative",
      "type": "boolean"
    },
    {
      "doc": "Flux in a 12 pixel radius aperture on the difference image.",
      "name": "apFlux",
      "type": "float"
    },
    {
      "doc": "Estimated uncertainty of apFlux.",
      "name": "apFluxErr",
      "type": "float"
    },
    {
      "doc": "General aperture flux algorithm failure flag; set if anything went wrong when measuring aperture fluxes. Another apFlux flag field should also be set to provide more information.",
      "name": "apFlux_flag",
      "type": "boolean"
    },
    {
      "doc": "Aperture did not fit within measurement image.",
      "name": "apFlux_flag_apertureTruncated",
      "type": "boolean"
    },
    {
      "doc": "The signal-to-noise ratio at which this source was detected in the difference image.",
      "name": "snr",
      "type": "float"
    },
    {
      "doc": "Flux for Point Source model. Note this actually measures the flux difference between the template and the visit image.",
      "name": "psfFlux",
      "type": "float"
    },
    {
      "doc": "Uncertainty of psfFlux.",
      "name": "psfFluxErr",
      "type": "float"
    },
    {
      "doc": "Right ascension coordinate of centroid for point source model.",
      "name": "psfRa",
      "type": "double"
    },
    {
      "doc": "Uncertainty of psfRa.",
      "name": "psfRaErr",
      "type": "float"
    },
    {
      "doc": "Declination coordinate of centroid for point source model.",
      "name": "psfDec",
      "type": "double"
    },
    {
      "doc": "Uncertainty of psfDec.",
      "name": "psfDecErr",
      "type": "float"
    },
    {
      "doc": "Covariance between psfFlux and psfRa.",
      "name": "psfFlux_psfRa_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance between psfFlux and psfDec.",
      "name": "psfFlux_psfDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance between psfRa and psfDec.",
      "name": "psfRa_psfDec_Cov",
      "type": "float"
    },
    {
      "doc": "Natural log likelihood of the observed data given the point source model.",
      "name": "psfLnL",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the point source model fit.",
      "name": "psfChi2",
      "type": "float"
    },
    {
      "doc": "The number of data points (pixels) used to fit the point source model.",
      "name": "psfNdata",
      "type": "int"
    },
    {
      "doc": "Failure to derive linear least-squares fit of psf model. Another psfFlux flag field should also be set to provide more information.",
      "name": "psfFlux_flag",
      "type": "boolean"
    },
    {
      "doc": "Object was too close to the edge of the image to use the full PSF model.",
      "name": "psfFlux_flag_edge",
      "type": "boolean"
    },
    {
      "doc": "Not enough non-rejected pixels in data to attempt the fit.",
      "name": "psfFlux_flag_noGoodPixels",
      "type": "boolean"
    },
    {
      "doc": "Flux for a trailed source model. Note this actually measures the flux difference between the template and the visit image.",
      "name": "trailFlux",
      "type": "float"
    },
    {
      "doc": "Uncertainty of trailFlux.",
      "name": "trailFluxErr",
      "type": "float"
    },
    {
      "doc": "Right ascension coordinate of centroid for trailed source model.",
      "name": "trailRa",
      "type": "double"
    },
    {
      "doc": "Uncertainty of trailRa.",
      "name": "trailRaErr",
      "type": "float"
    },
    {
      "doc": "Declination coordinate of centroid for trailed source model.",
      "name": "trailDec",
      "type": "double"
    },
    {
      "doc": "Uncertainty of trailDec.",
      "name": "trailDecErr",
      "type": "float"
    },
    {
      "doc": "Maximum likelihood fit of trail length.",
      "name": "trailLength",
      "type": "float"
    },
    {
      "doc": "Uncertainty of trailLength.",
      "name": "trailLengthErr",
      "type": "float"
    },
    {
      "doc": "Maximum likelihood fit of the angle between the meridian through the centroid and the trail direction (bearing).",
      "name": "trailAngle",
      "type": "float"
    },
    {
      "doc": "Uncertainty of trailAngle.",
      "name": "trailAngleErr",
      "type": "float"
    },
    {
      "doc": "Covariance of trailFlux and trailRa.",
      "name": "trailFlux_trailRa_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailFlux and trailDec.",
      "name": "trailFlux_trailDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailFlux and trailLength",
      "name": "trailFlux_trailLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailFlux and trailAngle",
      "name": "trailFlux_trailAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailRa and trailDec.",
      "name": "trailRa_trailDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailRa and trailLength.",
      "name": "trailRa_trailLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailRa and trailAngle.",
      "name": "trailRa_trailAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailDec and trailLength.",
      "name": "trailDec_trailLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailDec and trailAngle.",
      "name": "trailDec_trailAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of trailLength and trailAngle",
      "name": "trailLength_trailAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Natural log likelihood of the observed data given the trailed source model.",
      "name": "trailLnL",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the trailed source model fit.",
      "name": "trailChi2",
      "type": "float"
    },
    {
      "doc": "The number of data points (pixels) used to fit the trailed source model.",
      "name": "trailNdata",
      "type": "int"
    },
    {
      "doc": "This flag is set if a trailed source extends onto or past edge pixels.",
      "name": "trail_flag_edge",
      "type": "boolean"
    },
    {
      "doc": "Maximum likelihood value for the mean absolute flux of the two lobes for a dipole model.",
      "name": "dipoleMeanFlux",
      "type": "float"
    },
    {
      "doc": "Uncertainty of dipoleMeanFlux.",
      "name": "dipoleMeanFluxErr",
      "type": "float"
    },
    {
      "doc": "Maximum likelihood value for the difference of absolute fluxes of the two lobes for a dipole model.",
      "name": "dipoleFluxDiff",
      "type": "float"
    },
    {
      "doc": "Uncertainty of dipoleFluxDiff.",
      "name": "dipoleFluxDiffErr",
      "type": "float"
    },
    {
      "doc": "Right ascension coordinate of centroid for dipole model.",
      "name": "dipoleRa",
      "type": "double"
    },
    {
      "doc": "Uncertainty of dipoleRa.",
      "name": "dipoleRaErr",
      "type": "float"
    },
    {
      "doc": "Declination coordinate of centroid for dipole model.",
      "name": "dipoleDec",
      "type": "double"
    },
    {
      "doc": "Uncertainty of dipoleDec.",
      "name": "dipoleDecErr",
      "type": "float"
    },
    {
      "doc": "Maximum likelihood value for the lobe separation in dipole model.",
      "name": "dipoleLength",
      "type": "float"
    },
    {
      "doc": "Uncertainty of dipoleLength.",
      "name": "dipoleLengthErr",
      "type": "float"
    },
    {
      "doc": "Maximum likelihood fit of the angle between the meridian through the centroid and the dipole direction (bearing, from negative to positive lobe).",
      "name": "dipoleAngle",
      "type": "float"
    },
    {
      "doc": "Uncertainty of dipoleAngle.",
      "name": "dipoleAngleErr",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleMeanFlux and dipoleFluxDiff.",
      "name": "dipoleMeanFlux_dipoleFluxDiff_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleMeanFlux and dipoleRa.",
      "name": "dipoleMeanFlux_dipoleRa_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleMeanFlux and dipoleDec.",
      "name": "dipoleMeanFlux_dipoleDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleMeanFlux and dipoleLength.",
      "name": "dipoleMeanFlux_dipoleLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleMeanFlux and dipoleAngle.",
      "name": "dipoleMeanFlux_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleFluxDiff and dipoleRa.",
      "name": "dipoleFluxDiff_dipoleRa_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleFluxDiff and dipoleDec.",
      "name": "dipoleFluxDiff_dipoleDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleFluxDiff and dipoleLength.",
      "name": "dipoleFluxDiff_dipoleLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleFluxDiff and dipoleAngle.",
      "name": "dipoleFluxDiff_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleRa and dipoleDec.",
      "name": "dipoleRa_dipoleDec_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleRa and dipoleLength.",
      "name": "dipoleRa_dipoleLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleRa and dipoleAngle.",
      "name": "dipoleRa_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleDec and dipoleLength.",
      "name": "dipoleDec_dipoleLength_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleDec and dipoleAngle.",
      "name": "dipoleDec_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of dipoleLength and dipoleAngle.",
      "name": "dipoleLength_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "doc": "Natural log likelihood of the observed data given the dipole source model.",
      "name": "dipoleLnL",
      "type": "float"
    },
    {
      "doc": "Chi^2 statistic of the model fit.",
      "name": "dipoleChi2",
      "type": "float"
    },
    {
      "doc": "The number of data points (pixels) used to fit the model.",
      "name": "dipoleNdata",
      "type": "int"
    },
    {
      "doc": "Forced PSF photometry on science image failed. Another forced_PsfFlux flag field should also be set to provide more information.",
      "name": "forced_PsfFlux_flag",
      "type": "boolean"
    },
    {
      "doc": "Forced PSF flux on science image was too close to the edge of the image to use the full PSF model.",
      "name": "forced_PsfFlux_flag_edge",
      "type": "boolean"
    },
    {
      "doc": "Forced PSF flux not enough non-rejected pixels in data to attempt the fit.",
      "name": "forced_PsfFlux_flag_noGoodPixels",
      "type": "boolean"
    },
    {
      "doc": "Calibrated flux for Point Source model centered on radec but measured on the difference of snaps comprising this visit.",
      "name": "snapDiffFlux",
      "type": "float"
    },
    {
      "doc": "Estimated uncertainty of snapDiffFlux.",
      "name": "snapDiffFluxErr",
      "type": "float"
    },
    {
      "doc": "Estimated sky background at the position (centroid) of the object.",
      "name": "fpBkgd",
      "type": "float"
    },
    {
      "doc": "Estimated uncertainty of fpBkgd.",
      "name": "fpBkgdErr",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment of the source intensity.",
      "name": "ixx",
      "type": "float"
    },
    {
      "doc": "Uncertainty of ixx.",
      "name": "ixxErr",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment of the source intensity.",
      "name": "iyy",
      "type": "float"
    },
    {
      "doc": "Uncertainty of iyy.",
      "name": "iyyErr",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment of the source intensity.",
      "name": "ixy",
      "type": "float"
    },
    {
      "doc": "Uncertainty of ixy.",
      "name": "ixyErr",
      "type": "float"
    },
    {
      "doc": "Covariance of ixx and iyy.",
      "name": "ixx_iyy_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of ixx and ixy.",
      "name": "ixx_ixy_Cov",
      "type": "float"
    },
    {
      "doc": "Covariance of iyy and ixy.",
      "name": "iyy_ixy_Cov",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment for the PSF.",
      "name": "ixxPSF",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment for the PSF.",
      "name": "iyyPSF",
      "type": "float"
    },
    {
      "doc": "Adaptive second moment for the PSF.",
      "name": "ixyPSF",
      "type": "float"
    },
    {
      "doc": "General source shape algorithm failure flag; set if anything went wrong when measuring the shape. Another shape flag field should also be set to provide more information.",
      "name": "shape_flag",
      "type": "boolean"
    },
    {
      "doc": "No pixels to measure shape.",
      "name": "shape_flag_no_pixels",
      "type": "boolean"
    },
    {
      "doc": "Center not contained in footprint bounding box.",
      "name": "shape_flag_not_contained",
      "type": "boolean"
    },
    {
      "doc": "This source is a parent source; we should only be measuring on deblended children in difference imaging.",
      "name": "shape_flag_parent_source",
      "type": "boolean"
    },
    {
      "doc": "A measure of extendedness, computed by comparing an object's moment-based traced radius to the PSF moments. extendedness = 1 implies a high degree of confidence that the source is extended. extendedness = 0 implies a high degree of confidence that the source is point-like.",
      "name": "extendedness",
      "type": "float"
    },
    {
      "doc": "A measure of reliability, computed using information from the source and image characterization, as well as the information on the Telescope and Camera system (e.g., ghost maps, defect maps, etc.).",
      "name": "reliability",
      "type": "float"
    },
    {
      "doc": "Filter band this source was observed with.",
      "name": "band",
      "type": "string"
    },
    {
      "doc": "Attempted to fit a dipole model to this source.",
      "name": "dipoleFitAttempted",
      "type": "boolean"
    },
    {
      "doc": "General pixel flags failure; set if anything went wrong when setting pixels flags from this footprint's mask. This implies that some pixelFlags for this source may be incorrectly set to False.",
      "name": "pixelFlags",
      "type": "boolean"
    },
    {
      "doc": "Bad pixel in the DiaSource footprint.",
      "name": "pixelFlags_bad",
      "type": "boolean"
    },
    {
      "doc": "Cosmic ray in the DiaSource footprint.",
      "name": "pixelFlags_cr",
      "type": "boolean"
    },
    {
      "doc": "Cosmic ray in the 3x3 region around the centroid.",
      "name": "pixelFlags_crCenter",
      "type": "boolean"
    },
    {
      "doc": "Some of the source footprint is outside usable exposure region (masked EDGE or NO_DATA, or centroid off image).",
      "name": "pixelFlags_edge",
      "type": "boolean"
    },
    {
      "doc": "Interpolated pixel in the DiaSource footprint.",
      "name": "pixelFlags_interpolated",
      "type": "boolean"
    },
    {
      "doc": "Interpolated pixel in the 3x3 region around the centroid.",
      "name": "pixelFlags_interpolatedCenter",
      "type": "boolean"
    },
    {
      "doc": "DiaSource center is off image.",
      "name": "pixelFlags_offimage",
      "type": "boolean"
    },
    {
      "doc": "Saturated pixel in the DiaSource footprint.",
      "name": "pixelFlags_saturated",
      "type": "boolean"
    },
    {
      "doc": "Saturated pixel in the 3x3 region around the centroid.",
      "name": "pixelFlags_saturatedCenter",
      "type": "boolean"
    },
    {
      "doc": "DiaSource's footprint includes suspect pixels.",
      "name": "pixelFlags_suspect",
      "type": "boolean"
    },
    {
      "doc": "Suspect pixel in the 3x3 region around the centroid.",
      "name": "pixelFlags_suspectCenter",
      "type": "boolean"
    },
    {
      "doc": "Streak in the DiaSource footprint.",
      "name": "pixelFlags_streak",
      "type": "boolean"
    },
    {
      "doc": "Streak in the 3x3 region around the centroid.",
      "name": "pixelFlags_streakCenter",
      "type": "boolean"
    },
    {
      "doc": "Injection in the DiaSource footprint.",
      "name": "pixelFlags_injected",
      "type": "boolean"
    },
    {
      "doc": "Injection in the 3x3 region around the centroid.",
      "name": "pixelFlags_injectedCenter",
      "type": "boolean"
    },
    {
      "doc": "Template injection in the DiaSource footprint.",
      "name": "pixelFlags_injected_template",
      "type": "boolean"
    },
    {
      "doc": "Template injection in the 3x3 region around the centroid.",
      "name": "pixelFlags_injected_templateCenter",
      "type": "boolean"
    }
  ]
}