schema = {
  "name": "DP02_DiaSources",
  "fields": [
    {
      "name": "apFlux",
      "type": "double",
      "doc": "Flux within 12.0-pixel aperture"
    },
    {
      "name": "apFluxErr",
      "type": "double",
      "doc": "Flux uncertainty within 12.0-pixel aperture"
    },
    {
      "name": "apFlux_flag",
      "type": "boolean",
      "doc": "General Failure Flag"
    },
    {
      "name": "apFlux_flag_apertureTruncated",
      "type": "boolean",
      "doc": "Aperture did not fit within measurement image"
    },
    {
      "name": "bboxSize",
      "type": "long",
      "doc": "Bounding box of diaSource footprint"
    },
    {
      "name": "ccdVisitId",
      "type": "long",
      "doc": "Unique ID of CCD and visit where this source was detected and measured. Primary Key of the CcdVisit Table."
    },
    {
      "name": "centroid_flag",
      "type": "boolean",
      "doc": "General failure flag, set if anything went wrong"
    },
    {
      "name": "centroid_neg_flag",
      "type": "boolean",
      "doc": "Failure flag for negative, set if anything went wrong"
    },
    {
      "name": "centroid_pos_flag",
      "type": "boolean",
      "doc": "Failure flag for positive, set if anything went wrong"
    },
    {
      "name": "coord_dec",
      "type": "double",
      "doc": "Fiducial ICRS Declination of centroid used for database indexing"
    },
    {
      "name": "coord_ra",
      "type": "double",
      "doc": "Fiducial ICRS Right Ascension of centroid used for database indexing"
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Position in ra/dec"
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Unique DiaObject ID. Primary Key of the DIA Object Table"
    },
    {
      "name": "diaSourceId",
      "type": "long",
      "doc": "Unique ID"
    },
    {
      "name": "dipAngle",
      "type": "double",
      "doc": "Dipole orientation"
    },
    {
      "name": "dipChi2",
      "type": "double",
      "doc": "Chi2 per degree of freedom of dipole fit"
    },
    {
      "name": "dipFluxDiff",
      "type": "double",
      "doc": "Raw flux counts, positive lobe"
    },
    {
      "name": "dipFluxDiffErr",
      "type": "double",
      "doc": "Raw flux uncertainty counts, positive lobe"
    },
    {
      "name": "dipLength",
      "type": "double",
      "doc": "Pixel separation between positive and negative lobes of dipole"
    },
    {
      "name": "dipMeanFlux",
      "type": "double",
      "doc": "Raw flux counts, positive lobe"
    },
    {
      "name": "dipMeanFluxErr",
      "type": "double",
      "doc": "Raw flux uncertainty counts, positive lobe"
    },
    {
      "name": "filterName",
      "type": "char",
      "doc": "Band used to take this observation"
    },
    {
      "name": "forced_PsfFlux_flag",
      "type": "boolean",
      "doc": "Forced PSF flux general failure flag."
    },
    {
      "name": "forced_PsfFlux_flag_edge",
      "type": "boolean",
      "doc": "Forced PSF flux object was too close to the edge of the image to use the full PSF model."
    },
    {
      "name": "forced_PsfFlux_flag_noGoodPixels",
      "type": "boolean",
      "doc": "Forced PSF flux not enough non-rejected pixels in data to attempt the fit."
    },
    {
      "name": "isDipole",
      "type": "boolean",
      "doc": "Flag indicating diaSource is classified as a dipole"
    },
    {
      "name": "ixx",
      "type": "double",
      "doc": "Elliptical Gaussian adaptive moments"
    },
    {
      "name": "ixxPSF",
      "type": "double",
      "doc": "Adaptive moments of the PSF model at the object position"
    },
    {
      "name": "ixy",
      "type": "double",
      "doc": "Elliptical Gaussian adaptive moments"
    },
    {
      "name": "ixyPSF",
      "type": "double",
      "doc": "Adaptive moments of the PSF model at the object position"
    },
    {
      "name": "iyy",
      "type": "double",
      "doc": "Elliptical Gaussian adaptive moments"
    },
    {
      "name": "iyyPSF",
      "type": "double",
      "doc": "Adaptive moments of the PSF model at the object position"
    },
    {
      "name": "midPointTai",
      "type": "double",
      "doc": "Effective mid-exposure time for this diaSource."
    },
    {
      "name": "parentDiaSourceId",
      "type": "long",
      "doc": "Unique ID of parent source"
    },
    {
      "name": "pixelFlags",
      "type": "boolean",
      "doc": "General failure flag, set if anything went wrong"
    },
    {
      "name": "pixelFlags_bad",
      "type": "boolean",
      "doc": "Bad pixel in the Source footprint"
    },
    {
      "name": "pixelFlags_cr",
      "type": "boolean",
      "doc": "Cosmic ray in the Source footprint"
    },
    {
      "name": "pixelFlags_crCenter",
      "type": "boolean",
      "doc": "Cosmic ray in the Source center"
    },
    {
      "name": "pixelFlags_edge",
      "type": "boolean",
      "doc": "Source is outside usable exposure region (masked EDGE or NO_DATA)"
    },
    {
      "name": "pixelFlags_interpolated",
      "type": "boolean",
      "doc": "Interpolated pixel in the Source footprint"
    },
    {
      "name": "pixelFlags_interpolatedCenter",
      "type": "boolean",
      "doc": "Interpolated pixel in the Source center"
    },
    {
      "name": "pixelFlags_offimage",
      "type": "boolean",
      "doc": "Source center is off image"
    },
    {
      "name": "pixelFlags_saturated",
      "type": "boolean",
      "doc": "Saturated pixel in the Source footprint"
    },
    {
      "name": "pixelFlags_saturatedCenter",
      "type": "boolean",
      "doc": "Saturated pixel in the Source center"
    },
    {
      "name": "pixelFlags_suspect",
      "type": "boolean",
      "doc": "Sources footprint includes suspect pixels"
    },
    {
      "name": "pixelFlags_suspectCenter",
      "type": "boolean",
      "doc": "Sources center is close to suspect pixels"
    },
    {
      "name": "pixelId",
      "type": "long",
      "doc": "Position in ra/dec"
    },
    {
      "name": "psFlux",
      "type": "double",
      "doc": "Flux derived from linear least-squares fit of PSF model"
    },
    {
      "name": "psFluxErr",
      "type": "double",
      "doc": "Flux uncertainty derived from linear least-squares fit of PSF model"
    },
    {
      "name": "psfFlux_flag",
      "type": "boolean",
      "doc": "Failure to derive linear least-squares fit of psf model forced on the calexp"
    },
    {
      "name": "psfFlux_flag_edge",
      "type": "boolean",
      "doc": "Object was too close to the edge of the image to use the full PSF model"
    },
    {
      "name": "psfFlux_flag_noGoodPixels",
      "type": "boolean",
      "doc": "Not enough non-rejected pixels in data to attempt the fit"
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "Position in ra/dec"
    },
    {
      "name": "shape_flag",
      "type": "boolean",
      "doc": "General Failure Flag"
    },
    {
      "name": "shape_flag_maxIter",
      "type": "boolean",
      "doc": "Too many iterations in adaptive moments"
    },
    {
      "name": "shape_flag_psf",
      "type": "boolean",
      "doc": "Failure in measuring PSF model shape"
    },
    {
      "name": "shape_flag_shift",
      "type": "boolean",
      "doc": "Centroid shifted by more than the maximum allowed amount"
    },
    {
      "name": "shape_flag_unweighted",
      "type": "boolean",
      "doc": "Weighted moments converged to an invalid value; using unweighted moments"
    },
    {
      "name": "shape_flag_unweightedBad",
      "type": "boolean",
      "doc": "Both weighted and unweighted moments were invalid"
    },
    {
      "name": "snr",
      "type": "double",
      "doc": "Ratio of apFlux/apFluxErr"
    },
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "Id of the ssObject this source was associated with, if any. If not, it is set to 0"
    },
    {
      "name": "totFlux",
      "type": "double",
      "doc": "Forced PSF flux measured on the direct image."
    },
    {
      "name": "totFluxErr",
      "type": "double",
      "doc": "Forced PSF flux uncertainty measured on the direct image."
    },
    {
      "name": "x",
      "type": "double",
      "doc": "Unweighted first moment centroid, overall centroid"
    },
    {
      "name": "xErr",
      "type": "float",
      "doc": "1-sigma uncertainty on x position"
    },
    {
      "name": "y",
      "type": "double",
      "doc": "Unweighted first moment centroid, overall centroid"
    },
    {
      "name": "yErr",
      "type": "float",
      "doc": "1-sigma uncertainty on y position"
    }
  ],
  "indexes": ["PRIMARY KEY (diaObjectId, midPointTai, diaSourceId)"]
}
