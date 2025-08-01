schema = {
  'indexes':['PRIMARY KEY ("ssSourceId", "diaSourceId")'],
  "name": "ssSources",
  "fields": [
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "Unique identifier of the object."
    },
    {
      "name": "diaSourceId",
      "type": "long",
      "doc": "Unique identifier of the observation."
    },
    {
      "name": "mpcUniqueId",
      "type": "long",
      "doc": "MPC unique identifier of the observation."
    },
    {
      "name": "nearbyObj1",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObj2",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObj3",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObj4",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObj5",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObj6",
      "type": "long",
      "doc": "Closest Objects (3 stars and 3 galaxies) in Level 2 database."
    },
    {
      "name": "nearbyObjDist1",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjDist2",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjDist3",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjDist4",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjDist5",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjDist6",
      "type": "float",
      "doc": "Distances to nearbyObj."
    },
    {
      "name": "nearbyObjLnP1",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "nearbyObjLnP2",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "nearbyObjLnP3",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "nearbyObjLnP4",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "nearbyObjLnP5",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "nearbyObjLnP6",
      "type": "float",
      "doc": "Natural log of the probability that the observed DIAObject is the same as the nearby Object."
    },
    {
      "name": "eclipticLambda",
      "type": "double",
      "doc": "Ecliptic longitude."
    },
    {
      "name": "eclipticBeta",
      "type": "double",
      "doc": "Ecliptic latitude."
    },
    {
      "name": "galacticL",
      "type": "double",
      "doc": "Galactic longitude."
    },
    {
      "name": "galacticB",
      "type": "double",
      "doc": "Galactic latitute."
    },
    {
      "name": "phaseAngle",
      "type": "float",
      "doc": "Phase angle."
    },
    {
      "name": "heliocentricDist",
      "type": "float",
      "doc": "Heliocentric distance."
    },
    {
      "name": "topocentricDist",
      "type": "float",
      "doc": "Topocentric distace."
    },
    {
      "name": "predictedMagnitude",
      "type": "float",
      "doc": "Predicted magnitude."
    },
    {
      "name": "predictedMagnitudeSigma",
      "type": "float",
      "doc": "Prediction uncertainty (1-sigma)."
    },
    {
      "name": "residualRa",
      "type": "double",
      "doc": "Residual R.A. vs. ephemeris."
    },
    {
      "name": "residualDec",
      "type": "double",
      "doc": "Residual Dec vs. ephemeris."
    },
    {
      "name": "predictedRaSigma",
      "type": "float",
      "doc": "Predicted R.A. uncertainty."
    },
    {
      "name": "predictedDecSigma",
      "type": "float",
      "doc": "Predicted Dec uncertainty."
    },
    {
      "name": "predictedRaDecCov",
      "type": "float",
      "doc": "Predicted R.A./Dec covariance."
    },
    {
      "name": "heliocentricX",
      "type": "float",
      "doc": "Cartesian heliocentric X coordinate (at the emit time)."
    },
    {
      "name": "heliocentricY",
      "type": "float",
      "doc": "Cartesian heliocentric Y coordinate (at the emit time)."
    },
    {
      "name": "heliocentricZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z coordinate (at the emit time)."
    },
    {
      "name": "heliocentricVX",
      "type": "float",
      "doc": "Cartesian heliocentric X velocity (at the emit time)."
    },
    {
      "name": "heliocentricVY",
      "type": "float",
      "doc": "Cartesian heliocentric Y velocity (at the emit time)."
    },
    {
      "name": "heliocentricVZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z velocity (at the emit time)."
    },
    {
      "name": "topocentricX",
      "type": "float",
      "doc": "Cartesian topocentric X coordinate (at the emit time)."
    },
    {
      "name": "topocentricY",
      "type": "float",
      "doc": "Cartesian topocentric Y coordinate (at the emit time)."
    },
    {
      "name": "topocentricZ",
      "type": "float",
      "doc": "Cartesian topocentric Z coordinate (at the emit time)."
    },
    {
      "name": "topocentricVX",
      "type": "float",
      "doc": "Cartesian topocentric X velocity (at the emit time)."
    },
    {
      "name": "topocentricVY",
      "type": "float",
      "doc": "Cartesian topocentric Y velocity (at the emit time)."
    },
    {
      "name": "topocentricVZ",
      "type": "float",
      "doc": "Cartesian topocentric Z velocity (at the emit time)."
    }
  ]
}