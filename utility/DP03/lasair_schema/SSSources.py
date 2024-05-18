schema = {
  "name": "SSSources",
  "fields": [
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "Unique identifier of the object."
    },
    {
      "name": "diaSourceId",
      "type": "long",
      "doc": "Unique identifier of the observation"
    },
    {
      "name": "mpcUniqueId",
      "type": "long",
      "doc": "MPC unique identifier of the observation"
    },
    {
      "name": "eclipticLambda",
      "type": "double",
      "doc": "Ecliptic longitude"
    },
    {
      "name": "eclipticBeta",
      "type": "double",
      "doc": "Ecliptic latitude"
    },
    {
      "name": "galacticL",
      "type": "double",
      "doc": "Galactic longitude"
    },
    {
      "name": "galacticB",
      "type": "double",
      "doc": "Galactic latitute"
    },
    {
      "name": "phaseAngle",
      "type": "float",
      "doc": "Phase angle"
    },
    {
      "name": "heliocentricDist",
      "type": "float",
      "doc": "Heliocentric distance"
    },
    {
      "name": "topocentricDist",
      "type": "float",
      "doc": "Topocentric distace"
    },
    {
      "name": "predictedMagnitude",
      "type": "float",
      "doc": "Predicted magnitude"
    },
    {
      "name": "predictedMagnitudeErr",
      "type": "float",
      "doc": "Prediction uncertainty (1-sigma)"
    },
    {
      "name": "residualRa",
      "type": "double",
      "doc": "Residual R.A. vs. ephemeris"
    },
    {
      "name": "residualDec",
      "type": "double",
      "doc": "Residual Dec vs. ephemeris"
    },
    {
      "name": "predictedRaErr",
      "type": "float",
      "doc": "Predicted R.A. uncertainty"
    },
    {
      "name": "predictedDecErr",
      "type": "float",
      "doc": "Predicted Dec uncertainty"
    },
    {
      "name": "predictedRaDecCov",
      "type": "float",
      "doc": "Predicted R.A./Dec covariance"
    },
    {
      "name": "heliocentricX",
      "type": "float",
      "doc": "Cartesian heliocentric X coordinate (at the emit time)"
    },
    {
      "name": "heliocentricY",
      "type": "float",
      "doc": "Cartesian heliocentric Y coordinate (at the emit time)"
    },
    {
      "name": "heliocentricZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z coordinate (at the emit time)"
    },
    {
      "name": "heliocentricVX",
      "type": "float",
      "doc": "Cartesian heliocentric X velocity (at the emit time)"
    },
    {
      "name": "heliocentricVY",
      "type": "float",
      "doc": "Cartesian heliocentric Y velocity (at the emit time)"
    },
    {
      "name": "heliocentricVZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z velocity (at the emit time)"
    },
    {
      "name": "topocentricX",
      "type": "float",
      "doc": "Cartesian topocentric X coordinate (at the emit time)"
    },
    {
      "name": "topocentricY",
      "type": "float",
      "doc": "Cartesian topocentric Y coordinate (at the emit time)"
    },
    {
      "name": "topocentricZ",
      "type": "float",
      "doc": "Cartesian topocentric Z coordinate (at the emit time)"
    },
    {
      "name": "topocentricVX",
      "type": "float",
      "doc": "Cartesian topocentric X velocity (at the emit time)"
    },
    {
      "name": "topocentricVY",
      "type": "float",
      "doc": "Cartesian topocentric Y velocity (at the emit time)"
    },
    {
      "name": "topocentricVZ",
      "type": "float",
      "doc": "Cartesian topocentric Z velocity (at the emit time)"
    }
  ],
  "indexes": ["PRIMARY KEY (ssObjectId, diaSourceId)"]
}
