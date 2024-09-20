schema = {
  "name": "diaObjects",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long"
    },
    {
      "name": "ra",
      "type": "double"
    },
    {
      "name": "raErr",
      "type": "float"
    },
    {
      "name": "decl",
      "type": "double"
    },
    {
      "name": "decErr",
      "type": "float"
    },
    {
      "name": "ra_dec_Cov",
      "type": "float"
    },
    {
      "name": "radecMjdTai",
      "type": "double"
    },
    {
      "name": "pmRa",
      "type": "float"
    },
    {
      "name": "pmRaErr",
      "type": "float"
    },
    {
      "name": "pmDec",
      "type": "float"
    },
    {
      "name": "pmDecErr",
      "type": "float"
    },
    {
      "name": "parallax",
      "type": "float"
    },
    {
      "name": "parallaxErr",
      "type": "float"
    },
    {
      "name": "pmRa_pmDec_Cov",
      "type": "float"
    },
    {
      "name": "pmRa_parallax_Cov",
      "type": "float"
    },
    {
      "name": "pmDec_parallax_Cov",
      "type": "float"
    },
    {
      "name": "pmParallaxLnL",
      "type": "float"
    },
    {
      "name": "pmParallaxChi2",
      "type": "float"
    },
    {
      "name": "pmParallaxNdata",
      "type": "int"
    },
    {
      "name": "u_psfFluxMean",
      "type": "float"
    },
    {
      "name": "u_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "u_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "u_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "u_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "u_fpFluxMean",
      "type": "float"
    },
    {
      "name": "u_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "u_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "g_psfFluxMean",
      "type": "float"
    },
    {
      "name": "g_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "g_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "g_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "g_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "g_fpFluxMean",
      "type": "float"
    },
    {
      "name": "g_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "g_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "r_psfFluxMean",
      "type": "float"
    },
    {
      "name": "r_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "r_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "r_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "r_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "r_fpFluxMean",
      "type": "float"
    },
    {
      "name": "r_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "r_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "i_psfFluxMean",
      "type": "float"
    },
    {
      "name": "i_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "i_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "i_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "i_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "i_fpFluxMean",
      "type": "float"
    },
    {
      "name": "i_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "i_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "z_psfFluxMean",
      "type": "float"
    },
    {
      "name": "z_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "z_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "z_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "z_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "z_fpFluxMean",
      "type": "float"
    },
    {
      "name": "z_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "z_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "y_psfFluxMean",
      "type": "float"
    },
    {
      "name": "y_psfFluxMeanErr",
      "type": "float"
    },
    {
      "name": "y_psfFluxSigma",
      "type": "float"
    },
    {
      "name": "y_psfFluxChi2",
      "type": "float"
    },
    {
      "name": "y_psfFluxNdata",
      "type": "int"
    },
    {
      "name": "y_fpFluxMean",
      "type": "float"
    },
    {
      "name": "y_fpFluxMeanErr",
      "type": "float"
    },
    {
      "name": "y_fpFluxSigma",
      "type": "float"
    },
    {
      "name": "nearbyObj1",
      "type": "long"
    },
    {
      "name": "nearbyObj1Dist",
      "type": "float"
    },
    {
      "name": "nearbyObj1LnP",
      "type": "float"
    },
    {
      "name": "nearbyObj2",
      "type": "long"
    },
    {
      "name": "nearbyObj2Dist",
      "type": "float"
    },
    {
      "name": "nearbyObj2LnP",
      "type": "float"
    },
    {
      "name": "nearbyObj3",
      "type": "long"
    },
    {
      "name": "nearbyObj3Dist",
      "type": "float"
    },
    {
      "name": "nearbyObj3LnP",
      "type": "float"
    },
    {
      "name": "u_psfFluxErrMean",
      "type": "float"
    },
    {
      "name": "g_psfFluxErrMean",
      "type": "float"
    },
    {
      "name": "r_psfFluxErrMean",
      "type": "float"
    },
    {
      "name": "i_psfFluxErrMean",
      "type": "float"
    },
    {
      "name": "z_psfFluxErrMean",
      "type": "float"
    },
    {
      "name": "y_psfFluxErrMean",
      "type": "float"
    }
  ],
  "indexes": ['PRIMARY KEY ("diaObjectId")']
}
