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
      "name": "eclipticLambda",
      "type": "double",
      "doc": "Ecliptic longitude [deg]."
    },
    {
      "name": "eclipticBeta",
      "type": "double",
      "doc": "Ecliptic latitude [deg]."
    },
    {
      "name": "galacticL",
      "type": "double",
      "doc": "Galactic longitude [deg]."
    },
    {
      "name": "galacticB",
      "type": "double",
      "doc": "Galactic latitute [deg]."
    },
    {
      "name": "phaseAngle",
      "type": "float",
      "doc": "Phase angle [deg]."
    },
    {
      "name": "heliocentricDist",
      "type": "float",
      "doc": "Heliocentric distance [AU]."
    },
    {
      "name": "topocentricDist",
      "type": "float",
      "doc": "Topocentric distace [AU]."
    },
    {
      "name": "predictedVMagnitude",
      "type": "float",
      "doc": "Predicted V-band magnitude [mag]."
    },
    {
      "name": "residualRa",
      "type": "double",
      "doc": "Residual R.A. vs. ephemeris [deg]."
    },
    {
      "name": "residualDec",
      "type": "double",
      "doc": "Residual Dec vs. ephemeris [deg]."
    },
    {
      "name": "heliocentricX",
      "type": "float",
      "doc": "Cartesian heliocentric X coordinate (at the emit time) [AU]."
    },
    {
      "name": "heliocentricY",
      "type": "float",
      "doc": "Cartesian heliocentric Y coordinate (at the emit time) [AU]."
    },
    {
      "name": "heliocentricZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z coordinate (at the emit time) [AU]."
    },
    {
      "name": "heliocentricVX",
      "type": "float",
      "doc": "Cartesian heliocentric X velocity (at the emit time) [AU/d]."
    },
    {
      "name": "heliocentricVY",
      "type": "float",
      "doc": "Cartesian heliocentric Y velocity (at the emit time) [AU/d]."
    },
    {
      "name": "heliocentricVZ",
      "type": "float",
      "doc": "Cartesian heliocentric Z velocity (at the emit time) [AU/d]."
    },
    {
      "name": "topocentricX",
      "type": "float",
      "doc": "Cartesian topocentric X coordinate (at the emit time) [AU]."
    },
    {
      "name": "topocentricY",
      "type": "float",
      "doc": "Cartesian topocentric Y coordinate (at the emit time) [AU]."
    },
    {
      "name": "topocentricZ",
      "type": "float",
      "doc": "Cartesian topocentric Z coordinate (at the emit time) [AU]."
    },
    {
      "name": "topocentricVX",
      "type": "float",
      "doc": "Cartesian topocentric X velocity (at the emit time) [AU/d]."
    },
    {
      "name": "topocentricVY",
      "type": "float",
      "doc": "Cartesian topocentric Y velocity (at the emit time) [AU/d]."
    },
    {
      "name": "topocentricVZ",
      "type": "float",
      "doc": "Cartesian topocentric Z velocity (at the emit time) [AU/d]."
    }
  ]
}