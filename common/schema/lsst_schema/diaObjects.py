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
      "name": "ra",
      "type": "double",
      "doc": "Right ascension coordinate of the position of the object at time radecMjdTai."
    },
    {
      "name": "raErr",
      "type": "float",
      "doc": "Uncertainty of ra."
    },
    {
      "name": "decl",
      "type": "double",
      "doc": "Declination coordinate of the position of the object at time radecMjdTai."
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
      "name": "radecMjdTai",
      "type": "double",
      "doc": "Time at which the object was at a position ra/dec, expressed as Modified Julian Date, International Atomic Time."
    },
    {
      "name": "pmRa",
      "type": "float",
      "doc": "Proper motion in right ascension."
    },
    {
      "name": "pmRaErr",
      "type": "float",
      "doc": "Uncertainty of pmRa."
    },
    {
      "name": "pmDec",
      "type": "float",
      "doc": "Proper motion of declination."
    },
    {
      "name": "pmDecErr",
      "type": "float",
      "doc": "Uncertainty of pmDec."
    },
    {
      "name": "parallax",
      "type": "float",
      "doc": "Parallax."
    },
    {
      "name": "parallaxErr",
      "type": "float",
      "doc": "Uncertainty of parallax."
    },
    {
      "name": "pmRa_pmDec_Cov",
      "type": "float",
      "doc": "Covariance of pmRa and pmDec."
    },
    {
      "name": "pmRa_parallax_Cov",
      "type": "float",
      "doc": "Covariance of pmRa and parallax."
    },
    {
      "name": "pmDec_parallax_Cov",
      "type": "float",
      "doc": "Covariance of pmDec and parallax."
    },
    {
      "name": "pmParallaxLnL",
      "type": "float",
      "doc": "Natural log of the likelihood of the linear proper motion parallax fit."
    },
    {
      "name": "pmParallaxChi2",
      "type": "float",
      "doc": "Chi^2 static of the model fit."
    },
    {
      "name": "pmParallaxNdata",
      "type": "int",
      "doc": "The number of data points used to fit the model."
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
      "name": "u_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of u_fpFlux."
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
      "name": "g_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of g_fpFlux."
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
      "name": "r_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of r_fpFlux."
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
      "name": "i_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of i_fpFlux."
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
      "name": "z_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of z_fpFlux."
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
      "name": "y_fpFluxSigma",
      "type": "float",
      "doc": "Standard deviation of the distribution of y_fpFlux."
    },
    {
      "name": "nearbyObj1",
      "type": "long",
      "doc": "Id of the closest nearby object."
    },
    {
      "name": "nearbyObj1Dist",
      "type": "float",
      "doc": "Distance to nearbyObj1."
    },
    {
      "name": "nearbyObj1LnP",
      "type": "float",
      "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj1."
    },
    {
      "name": "nearbyObj2",
      "type": "long",
      "doc": "Id of the second-closest nearby object."
    },
    {
      "name": "nearbyObj2Dist",
      "type": "float",
      "doc": "Distance to nearbyObj2."
    },
    {
      "name": "nearbyObj2LnP",
      "type": "float",
      "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj2."
    },
    {
      "name": "nearbyObj3",
      "type": "long",
      "doc": "Id of the third-closest nearby object."
    },
    {
      "name": "nearbyObj3Dist",
      "type": "float",
      "doc": "Distance to nearbyObj3."
    },
    {
      "name": "nearbyObj3LnP",
      "type": "float",
      "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj3."
    },
    {
      "name": "u_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the u band flux errors."
    },
    {
      "name": "g_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the g band flux errors."
    },
    {
      "name": "r_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the r band flux errors."
    },
    {
      "name": "i_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the i band flux errors."
    },
    {
      "name": "z_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the z band flux errors."
    },
    {
      "name": "y_psfFluxErrMean",
      "type": "float",
      "doc": "Mean of the y band flux errors."
    }
  ]
}