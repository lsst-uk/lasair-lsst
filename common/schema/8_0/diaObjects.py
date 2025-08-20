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
      "name": "validityStart",
      "type": "long",
      "doc": "Processing time when validity of this diaObject starts."
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "Right ascension coordinate of the position of the object."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Declination coordinate of the position of the object."
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
      "name": "u_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for u filter."
    },
    {
      "name": "u_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of u_psfFluxMean."
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
      "name": "g_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for g filter."
    },
    {
      "name": "g_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of g_psfFluxMean."
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
      "name": "r_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for r filter."
    },
    {
      "name": "r_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of r_psfFluxMean."
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
      "name": "i_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for i filter."
    },
    {
      "name": "i_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of i_psfFluxMean."
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
      "name": "z_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for z filter."
    },
    {
      "name": "z_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of z_psfFluxMean."
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
      "name": "y_psfFluxMean",
      "type": "float",
      "doc": "Weighted mean point-source model magnitude for y filter."
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float",
      "doc": "Standard error of y_psfFluxMean."
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
      "name": "firstDiaSourceMjdTai",
      "type": "double",
      "doc": "Time of the first diaSource, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "nDiaSources",
      "type": "int",
      "doc": "Total number of DiaSources associated with this DiaObject."
    }
  ]
}