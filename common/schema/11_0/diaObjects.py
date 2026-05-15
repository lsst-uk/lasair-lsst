schema = {
  'indexes':['PRIMARY KEY ("diaObjectId")'],
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
      "doc": "Right ascension coordinate of the position of the object [deg]."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra [deg]."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Declination coordinate of the position of the object [deg]."
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
      "name": "u_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for u filter [nJy]."
    },
    {
      "name": "u_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_psfFluxMean [nJy]."
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
      "name": "g_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for g filter [nJy]."
    },
    {
      "name": "g_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_psfFluxMean [nJy]."
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
      "name": "r_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for r filter [nJy]."
    },
    {
      "name": "r_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_psfFluxMean [nJy]."
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
      "name": "i_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for i filter [nJy]."
    },
    {
      "name": "i_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_psfFluxMean [nJy]."
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
      "name": "z_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for z filter [nJy]."
    },
    {
      "name": "z_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_psfFluxMean [nJy]."
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
      "name": "y_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for y filter [nJy]."
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_psfFluxMean [nJy]."
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
    },
    {
      "name": "firstDiaSourceMjdTai",
      "type": "double",
      "doc": "Time of the first diaSource, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "lastDiaSourceMjdTai",
      "type": "double",
      "doc": "Time of the most recent non-forced DIASource for this object, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "nDiaSources",
      "type": "int",
      "doc": "Total number of DiaSources associated with this DiaObject."
    }
  ]
}