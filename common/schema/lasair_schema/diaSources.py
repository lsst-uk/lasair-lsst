schema = {
  "name": "diaSources",
  "fields": [
    {
      "name": "diaSourceId",
      "type": "long"
    },
    {
      "name": "ccdVisitId",
      "type": "long"
    },
    {
      "name": "diaObjectId",
      "type": "long"
    },
    {
      "name": "ssObjectId",
      "type": "long"
    },
    {
      "name": "parentDiaSourceId",
      "type": "long"
    },
    {
      "name": "midpointMjdTai",
      "type": "double"
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
      "name": "x",
      "type": "float"
    },
    {
      "name": "xErr",
      "type": "float"
    },
    {
      "name": "y",
      "type": "float"
    },
    {
      "name": "yErr",
      "type": "float"
    },
    {
      "name": "x_y_Cov",
      "type": "float"
    },
    {
      "name": "apFlux",
      "type": "float"
    },
    {
      "name": "apFluxErr",
      "type": "float"
    },
    {
      "name": "snr",
      "type": "float"
    },
    {
      "name": "psfFlux",
      "type": "float"
    },
    {
      "name": "psfFluxErr",
      "type": "float"
    },
    {
      "name": "psfRa",
      "type": "double"
    },
    {
      "name": "psfRaErr",
      "type": "float"
    },
    {
      "name": "psfDec",
      "type": "double"
    },
    {
      "name": "psfDecErr",
      "type": "float"
    },
    {
      "name": "psfFlux_psfRa_Cov",
      "type": "float"
    },
    {
      "name": "psfFlux_psfDec_Cov",
      "type": "float"
    },
    {
      "name": "psfRa_psfDec_Cov",
      "type": "float"
    },
    {
      "name": "psfLnL",
      "type": "float"
    },
    {
      "name": "psfChi2",
      "type": "float"
    },
    {
      "name": "psfNdata",
      "type": "int"
    },
    {
      "name": "trailFlux",
      "type": "float"
    },
    {
      "name": "trailFluxErr",
      "type": "float"
    },
    {
      "name": "trailRa",
      "type": "double"
    },
    {
      "name": "trailRaErr",
      "type": "float"
    },
    {
      "name": "trailDec",
      "type": "double"
    },
    {
      "name": "trailDecErr",
      "type": "float"
    },
    {
      "name": "trailLength",
      "type": "float"
    },
    {
      "name": "trailLengthErr",
      "type": "float"
    },
    {
      "name": "trailAngle",
      "type": "float"
    },
    {
      "name": "trailAngleErr",
      "type": "float"
    },
    {
      "name": "trailFlux_trailRa_Cov",
      "type": "float"
    },
    {
      "name": "trailFlux_trailDec_Cov",
      "type": "float"
    },
    {
      "name": "trailFlux_trailLength_Cov",
      "type": "float"
    },
    {
      "name": "trailFlux_trailAngle_Cov",
      "type": "float"
    },
    {
      "name": "trailRa_trailDec_Cov",
      "type": "float"
    },
    {
      "name": "trailRa_trailLength_Cov",
      "type": "float"
    },
    {
      "name": "trailRa_trailAngle_Cov",
      "type": "float"
    },
    {
      "name": "trailDec_trailLength_Cov",
      "type": "float"
    },
    {
      "name": "trailDec_trailAngle_Cov",
      "type": "float"
    },
    {
      "name": "trailLength_trailAngle_Cov",
      "type": "float"
    },
    {
      "name": "trailLnL",
      "type": "float"
    },
    {
      "name": "trailChi2",
      "type": "float"
    },
    {
      "name": "trailNdata",
      "type": "int"
    },
    {
      "name": "dipoleMeanFlux",
      "type": "float"
    },
    {
      "name": "dipoleMeanFluxErr",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiff",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiffErr",
      "type": "float"
    },
    {
      "name": "dipoleRa",
      "type": "double"
    },
    {
      "name": "dipoleRaErr",
      "type": "float"
    },
    {
      "name": "dipoleDec",
      "type": "double"
    },
    {
      "name": "dipoleDecErr",
      "type": "float"
    },
    {
      "name": "dipoleLength",
      "type": "float"
    },
    {
      "name": "dipoleLengthErr",
      "type": "float"
    },
    {
      "name": "dipoleAngle",
      "type": "float"
    },
    {
      "name": "dipoleAngleErr",
      "type": "float"
    },
    {
      "name": "dipoleMeanFlux_dipoleFluxDiff_Cov",
      "type": "float"
    },
    {
      "name": "dipoleMeanFlux_dipoleRa_Cov",
      "type": "float"
    },
    {
      "name": "dipoleMeanFlux_dipoleDec_Cov",
      "type": "float"
    },
    {
      "name": "dipoleMeanFlux_dipoleLength_Cov",
      "type": "float"
    },
    {
      "name": "dipoleMeanFlux_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiff_dipoleRa_Cov",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiff_dipoleDec_Cov",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiff_dipoleLength_Cov",
      "type": "float"
    },
    {
      "name": "dipoleFluxDiff_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipoleRa_dipoleDec_Cov",
      "type": "float"
    },
    {
      "name": "dipoleRa_dipoleLength_Cov",
      "type": "float"
    },
    {
      "name": "dipoleRa_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipoleDec_dipoleLength_Cov",
      "type": "float"
    },
    {
      "name": "dipoleDec_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipoleLength_dipoleAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipoleLnL",
      "type": "float"
    },
    {
      "name": "dipoleChi2",
      "type": "float"
    },
    {
      "name": "dipoleNdata",
      "type": "int"
    },
    {
      "name": "snapDiffFlux",
      "type": "float"
    },
    {
      "name": "snapDiffFluxErr",
      "type": "float"
    },
    {
      "name": "fpBkgd",
      "type": "float"
    },
    {
      "name": "fpBkgdErr",
      "type": "float"
    },
    {
      "name": "ixx",
      "type": "float"
    },
    {
      "name": "ixxErr",
      "type": "float"
    },
    {
      "name": "iyy",
      "type": "float"
    },
    {
      "name": "iyyErr",
      "type": "float"
    },
    {
      "name": "ixy",
      "type": "float"
    },
    {
      "name": "ixyErr",
      "type": "float"
    },
    {
      "name": "ixx_iyy_Cov",
      "type": "float"
    },
    {
      "name": "ixx_ixy_Cov",
      "type": "float"
    },
    {
      "name": "iyy_ixy_Cov",
      "type": "float"
    },
    {
      "name": "ixxPSF",
      "type": "float"
    },
    {
      "name": "iyyPSF",
      "type": "float"
    },
    {
      "name": "ixyPSF",
      "type": "float"
    },
    {
      "name": "extendedness",
      "type": "float"
    },
    {
      "name": "reliability",
      "type": "float"
    },
    {
      "name": "flags",
      "type": "long"
    },
    {
      "name": "band",
      "type": "string"
    }
  ],
  "indexes": ["PRIMARY KEY (diaObjectId, midPointMjdTai, diaSourceId)"]
}
