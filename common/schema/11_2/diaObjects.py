schema = {

  "indexes": [
    "PRIMARY KEY (\"diaObjectId\")"
  ],
  "name": "diaObjects",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Unique identifier of this DiaObject."
    },
    {
      "name": "validityStartMjdTai",
      "type": "double",
      "doc": "Processing time when validity of this diaObject starts, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "Right ascension of the inverse-variance weighted mean position of the DiaSources associated with this object, from all bands."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Angular error of Right Ascension (dRA*cos(Dec)) [deg]."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Declination coordinate of the position of the object [deg]."
    },
    {
      "name": "decErr",
      "type": "float",
      "doc": "Angular error of Declination."
    },
    {
      "name": "ra_dec_Cov",
      "type": "float",
      "doc": "Covariance between the mean ra (RA*cos(Dec)) and dec."
    },
    {
      "name": "u_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the u-band DiaSources."
    },
    {
      "name": "u_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of u_psfFluxMean."
    },
    {
      "name": "u_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the u-band DiaSources."
    },
    {
      "name": "u_psfFluxNdata",
      "type": "int",
      "doc": "Number of u-band DiaSources used to compute u_psfFluxMean."
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
      "name": "g_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the g-band DiaSources."
    },
    {
      "name": "g_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of g_psfFluxMean."
    },
    {
      "name": "g_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the g-band DiaSources."
    },
    {
      "name": "g_psfFluxNdata",
      "type": "int",
      "doc": "Number of g-band DiaSources used to compute g_psfFluxMean."
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
      "name": "r_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the r-band DiaSources."
    },
    {
      "name": "r_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of r_psfFluxMean."
    },
    {
      "name": "r_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the r-band DiaSources."
    },
    {
      "name": "r_psfFluxNdata",
      "type": "int",
      "doc": "Number of r-band DiaSources used to compute r_psfFluxMean."
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
      "name": "i_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the i-band DiaSources."
    },
    {
      "name": "i_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of i_psfFluxMean."
    },
    {
      "name": "i_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the i-band DiaSources."
    },
    {
      "name": "i_psfFluxNdata",
      "type": "int",
      "doc": "Number of i-band DiaSources used to compute i_psfFluxMean."
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
      "name": "z_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the z-band DiaSources."
    },
    {
      "name": "z_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of z_psfFluxMean."
    },
    {
      "name": "z_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the z-band DiaSources."
    },
    {
      "name": "z_psfFluxNdata",
      "type": "int",
      "doc": "Number of z-band DiaSources used to compute z_psfFluxMean."
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
      "name": "y_psfFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of psfFlux of the y-band DiaSources."
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of y_psfFluxMean."
    },
    {
      "name": "y_psfFluxSigma",
      "type": "float",
      "doc": "Unweighted sample standard deviation of psfFlux of the y-band DiaSources."
    },
    {
      "name": "y_psfFluxNdata",
      "type": "int",
      "doc": "Number of y-band DiaSources used to compute y_psfFluxMean."
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
      "doc": "Inverse-variance weighted mean of scienceFlux of the u-band DiaSources."
    },
    {
      "name": "u_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of u_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "g_scienceFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of scienceFlux of the g-band DiaSources."
    },
    {
      "name": "g_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of g_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "r_scienceFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of scienceFlux of the r-band DiaSources."
    },
    {
      "name": "r_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of r_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "i_scienceFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of scienceFlux of the i-band DiaSources."
    },
    {
      "name": "i_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of i_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "z_scienceFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of scienceFlux of the z-band DiaSources."
    },
    {
      "name": "z_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of z_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "y_scienceFluxMean",
      "type": "float",
      "doc": "Inverse-variance weighted mean of scienceFlux of the y-band DiaSources."
    },
    {
      "name": "y_scienceFluxMeanErr",
      "type": "float",
      "doc": "Uncertainty of y_scienceFluxMean, sqrt(1/sum(scienceFluxErr**-2))."
    },
    {
      "name": "u_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the u-band DiaSources."
    },
    {
      "name": "u_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the u-band DiaSources."
    },
    {
      "name": "u_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive u-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "u_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the u-band DiaSources."
    },
    {
      "name": "g_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the g-band DiaSources."
    },
    {
      "name": "g_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the g-band DiaSources."
    },
    {
      "name": "g_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive g-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "g_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the g-band DiaSources."
    },
    {
      "name": "r_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the r-band DiaSources."
    },
    {
      "name": "r_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the r-band DiaSources."
    },
    {
      "name": "r_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive r-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "r_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the r-band DiaSources."
    },
    {
      "name": "i_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the i-band DiaSources."
    },
    {
      "name": "i_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the i-band DiaSources."
    },
    {
      "name": "i_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive i-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "i_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the i-band DiaSources."
    },
    {
      "name": "z_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the z-band DiaSources."
    },
    {
      "name": "z_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the z-band DiaSources."
    },
    {
      "name": "z_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive z-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "z_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the z-band DiaSources."
    },
    {
      "name": "y_psfFluxMin",
      "type": "float",
      "doc": "Minimum psfFlux of the y-band DiaSources."
    },
    {
      "name": "y_psfFluxMax",
      "type": "float",
      "doc": "Maximum psfFlux of the y-band DiaSources."
    },
    {
      "name": "y_psfFluxMaxSlope",
      "type": "float",
      "doc": "Largest amplitude of change of psfFlux between consecutive y-band DiaSources, max(delta_flux/delta_time); positive values are brightening."
    },
    {
      "name": "y_psfFluxErrMean",
      "type": "float",
      "doc": "Unweighted mean of psfFluxErr of the y-band DiaSources."
    },
    {
      "name": "firstDiaSourceMjdTai",
      "type": "double",
      "doc": "midpointMjdTai of the earliest DiaSource associated with this object, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "lastDiaSourceMjdTai",
      "type": "double",
      "doc": "midpointMjdTai of the most recent DiaSource associated with this object, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "nDiaSources",
      "type": "int",
      "doc": "Number of DiaSources, in all bands, associated with this DiaObject in the APDB history window (360 days by default) up to and including this one."
    }
  ]
}