schema = {
  "name": "ForcedSourceOnDiaObjects",
  "fields": [
    {
      "name": "band",
      "type": "string",
      "doc": "Abstract filter that is not associated with a particular instrument"
    },
    {
      "name": "ccdVisitId",
      "type": "long",
      "doc": "Unique ID of visit and detector for which forced photometry was performed. Primary Key of the CcdVisit Table."
    },
    {
      "name": "coord_dec",
      "type": "double",
      "doc": "Fiducial ICRS Declination of DiaObject centroid used for database indexing"
    },
    {
      "name": "coord_ra",
      "type": "double",
      "doc": "Fiducial ICRS Right Ascension of DiaObject centroid used for database indexing"
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Unique DiaObject ID. Primary Key of the DiaObject Table"
    },
    {
      "name": "filterName",
      "type": "string",
      "doc": "Filter name copied from CcdVisit"
    },
    {
      "name": "forcedSourceOnDiaObjectId",
      "type": "long",
      "doc": "Unique ID of forced source. Primary Key."
    },
    {
      "name": "localBackground_instFlux",
      "type": "double",
      "doc": "Background in annulus around source"
    },
    {
      "name": "localBackground_instFluxErr",
      "type": "double",
      "doc": "1-sigma uncertainty on the background in an annulus around source"
    },
    {
      "name": "localPhotoCalib",
      "type": "double",
      "doc": "Local approximation of the PhotoCalib calibration factor at the location of the src."
    },
    {
      "name": "localPhotoCalibErr",
      "type": "double",
      "doc": "Error on the local approximation of the PhotoCalib calibration factor at the location of the src."
    },
    {
      "name": "localPhotoCalib_flag",
      "type": "boolean",
      "doc": "Set for any fatal failure"
    },
    {
      "name": "localWcs_CDMatrix_1_1",
      "type": "double",
      "doc": "(1, 1) element of the CDMatrix for the linear approximation of the WCS at the src location. Gives units in radians."
    },
    {
      "name": "localWcs_CDMatrix_1_2",
      "type": "double",
      "doc": "(1, 2) element of the CDMatrix for the linear approximation of the WCS at the src location. Gives units in radians."
    },
    {
      "name": "localWcs_CDMatrix_2_1",
      "type": "double",
      "doc": "(2, 1) element of the CDMatrix for the linear approximation of the WCS at the src location. Gives units in radians."
    },
    {
      "name": "localWcs_CDMatrix_2_2",
      "type": "double",
      "doc": "(2, 2) element of the CDMatrix for the linear approximation of the WCS at the src location. Gives units in radians."
    },
    {
      "name": "localWcs_flag",
      "type": "boolean",
      "doc": "Set for any fatal failure"
    },
    {
      "name": "midPointTai",
      "type": "double",
      "doc": "MJD of visit (added by Lasair)"
    },
    {
      "name": "parentObjectId",
      "type": "long",
      "doc": "Unique ObjectId of the parent of the ObjectId in context of the deblender."
    },
    {
      "name": "patch",
      "type": "long",
      "doc": "Skymap patch ID"
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
      "name": "psfDiffFlux",
      "type": "double",
      "doc": "Flux derived from linear least-squares fit of psf model forced on the image difference"
    },
    {
      "name": "psfDiffFluxErr",
      "type": "double",
      "doc": "Uncertainty on the flux derived from linear least-squares fit of psf model forced on the image difference"
    },
    {
      "name": "psfDiffFlux_flag",
      "type": "boolean",
      "doc": "Failure to derive linear least-squares fit of psf model forced on the image difference"
    },
    {
      "name": "psFlux",
      "type": "double",
      "doc": "Flux derived from linear least-squares fit of psf model forced on the calexp (was psfFlux)"
    },
    {
      "name": "psFluxErr",
      "type": "double",
      "doc": "Uncertainty on the flux derived from linear least-squares fit of psf model forced on the calexp (was psfFluxErr)"
    },
    {
      "name": "psfFlux_flag",
      "type": "boolean",
      "doc": "Failure to derive linear least-squares fit of psf model forced on the calexp"
    },
    {
      "name": "skymap",
      "type": "string",
      "doc": "Name of skymap used for coadd projection"
    },
    {
      "name": "tract",
      "type": "long",
      "doc": "Skymap tract ID"
    }
  ],
  "indexes": ["PRIMARY KEY (diaObjectId)"]
}
