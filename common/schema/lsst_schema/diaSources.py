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
      "name": "midPointTai",
      "type": "double"
    },
    {
      "name": "filterName",
      "type": "string"
    },
    {
      "name": "programId",
      "type": "int"
    },
    {
      "name": "ra",
      "type": "double"
    },
    {
      "name": "decl",
      "type": "double"
    },
    {
      "name": "raErr",
      "type": "float"
    },
    {
      "name": "declErr",
      "type": "float"
    },
    {
      "name": "ra_decl_Cov",
      "type": "float"
    },
    {
      "name": "x",
      "type": "float"
    },
    {
      "name": "y",
      "type": "float"
    },
    {
      "name": "xErr",
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
      "name": "psFlux",
      "type": "float"
    },
    {
      "name": "psFluxErr",
      "type": "float"
    },
    {
      "name": "psRa",
      "type": "double"
    },
    {
      "name": "psDecl",
      "type": "double"
    },
    {
      "name": "psRaErr",
      "type": "float"
    },
    {
      "name": "psDeclErr",
      "type": "float"
    },
    {
      "name": "psFlux_psRa_Cov",
      "type": "float"
    },
    {
      "name": "psFlux_psDecl_Cov",
      "type": "float"
    },
    {
      "name": "psRa_psDecl_Cov",
      "type": "float"
    },
    {
      "name": "psLnL",
      "type": "float"
    },
    {
      "name": "psChi2",
      "type": "float"
    },
    {
      "name": "psNdata",
      "type": "int"
    },
    {
      "name": "trailFlux",
      "type": "float"
    },
    {
      "name": "trailRa",
      "type": "double"
    },
    {
      "name": "trailDecl",
      "type": "double"
    },
    {
      "name": "trailLength",
      "type": "float"
    },
    {
      "name": "trailAngle",
      "type": "float"
    },
    {
      "name": "trailFluxErr",
      "type": "float"
    },
    {
      "name": "trailRaErr",
      "type": "float"
    },
    {
      "name": "trailDeclErr",
      "type": "float"
    },
    {
      "name": "trailLengthErr",
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
      "name": "trailFlux_trailDecl_Cov",
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
      "name": "trailRa_trailDecl_Cov",
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
      "name": "trailDecl_trailLength_Cov",
      "type": "float"
    },
    {
      "name": "trailDecl_trailAngle_Cov",
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
      "name": "dipMeanFlux",
      "type": "float"
    },
    {
      "name": "dipFluxDiff",
      "type": "float"
    },
    {
      "name": "dipRa",
      "type": "double"
    },
    {
      "name": "dipDecl",
      "type": "double"
    },
    {
      "name": "dipLength",
      "type": "float"
    },
    {
      "name": "dipAngle",
      "type": "float"
    },
    {
      "name": "dipMeanFluxErr",
      "type": "float"
    },
    {
      "name": "dipFluxDiffErr",
      "type": "float"
    },
    {
      "name": "dipRaErr",
      "type": "float"
    },
    {
      "name": "dipDeclErr",
      "type": "float"
    },
    {
      "name": "dipLengthErr",
      "type": "float"
    },
    {
      "name": "dipAngleErr",
      "type": "float"
    },
    {
      "name": "dipMeanFlux_dipFluxDiff_Cov",
      "type": "float"
    },
    {
      "name": "dipMeanFlux_dipRa_Cov",
      "type": "float"
    },
    {
      "name": "dipMeanFlux_dipDecl_Cov",
      "type": "float"
    },
    {
      "name": "dipMeanFlux_dipLength_Cov",
      "type": "float"
    },
    {
      "name": "dipMeanFlux_dipAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipFluxDiff_dipRa_Cov",
      "type": "float"
    },
    {
      "name": "dipFluxDiff_dipDecl_Cov",
      "type": "float"
    },
    {
      "name": "dipFluxDiff_dipLength_Cov",
      "type": "float"
    },
    {
      "name": "dipFluxDiff_dipAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipRa_dipDecl_Cov",
      "type": "float"
    },
    {
      "name": "dipRa_dipLength_Cov",
      "type": "float"
    },
    {
      "name": "dipRa_dipAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipDecl_dipLength_Cov",
      "type": "float"
    },
    {
      "name": "dipDecl_dipAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipLength_dipAngle_Cov",
      "type": "float"
    },
    {
      "name": "dipLnL",
      "type": "float"
    },
    {
      "name": "dipChi2",
      "type": "float"
    },
    {
      "name": "dipNdata",
      "type": "int"
    },
    {
      "name": "totFlux",
      "type": "float"
    },
    {
      "name": "totFluxErr",
      "type": "float"
    },
    {
      "name": "diffFlux",
      "type": "float"
    },
    {
      "name": "diffFluxErr",
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
      "name": "iyy",
      "type": "float"
    },
    {
      "name": "ixy",
      "type": "float"
    },
    {
      "name": "ixxErr",
      "type": "float"
    },
    {
      "name": "iyyErr",
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
      "name": "spuriousness",
      "type": "float"
    },
    {
      "name": "flags",
      "type": "long"
    }
  ],
  "indexes": []
}