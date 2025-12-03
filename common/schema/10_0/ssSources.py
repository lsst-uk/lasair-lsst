schema = {
  'indexes':['PRIMARY KEY ("ssObjectId", "diaSourceId")'],
  "name": "ssSources",
  "fields": [
    {
      "name": "diaSourceId",
      "type": "long",
      "doc": "Unique identifier of the observation (matching DiaSource.diaSourceId)."
    },
    {
      "name": "ssObjectId",
      "type": "long",
      "doc": "Unique LSST identifier of the Solar System object."
    },
    {
      "name": "designation",
      "type": "string",
      "doc": "The unpacked primary provisional designation for this object."
    },
    {
      "name": "eclLambda",
      "type": "double",
      "doc": "Ecliptic longitude, converted from the observed coordinates."
    },
    {
      "name": "eclBeta",
      "type": "double",
      "doc": "Ecliptic latitude, converted from the observed coordinates."
    },
    {
      "name": "galLon",
      "type": "double",
      "doc": "Galactic longitude, converted from the observed coordinates."
    },
    {
      "name": "galLat",
      "type": "double",
      "doc": "Galactic latitude, converted from the observed coordinates."
    },
    {
      "name": "elongation",
      "type": "float",
      "doc": "Solar elongation of the object at the time of observation."
    },
    {
      "name": "phaseAngle",
      "type": "float",
      "doc": "Phase angle between the Sun, object, and observer."
    },
    {
      "name": "topoRange",
      "type": "float",
      "doc": "Topocentric distance (delta) at light-emission time."
    },
    {
      "name": "topoRangeRate",
      "type": "float",
      "doc": "Topocentric radial (line-of-sight) velocity (deldot); positive values indicate motion away from the observer."
    },
    {
      "name": "helioRange",
      "type": "float",
      "doc": "Heliocentric distance (r) at light-emission time."
    },
    {
      "name": "helioRangeRate",
      "type": "float",
      "doc": "Heliocentric radial velocity (rdot); positive values indicate motion away from the Sun."
    },
    {
      "name": "ephRa",
      "type": "double",
      "doc": "Predicted ICRS right ascension from the orbit in mpc_orbits."
    },
    {
      "name": "ephDec",
      "type": "double",
      "doc": "Predicted ICRS declination from the orbit in mpc_orbits."
    },
    {
      "name": "ephVmag",
      "type": "float",
      "doc": "Predicted magnitude in V band, computed from mpc_orbits data including the mpc_orbits-provided (H, G) estimates\n"
    },
    {
      "name": "ephRate",
      "type": "float",
      "doc": "Total predicted on-sky angular rate of motion."
    },
    {
      "name": "ephRateRa",
      "type": "float",
      "doc": "Predicted on-sky angular rate in the R.A. direction (includes the cos(dec) factor)."
    },
    {
      "name": "ephRateDec",
      "type": "float",
      "doc": "Predicted on-sky angular rate in the declination direction."
    },
    {
      "name": "ephOffset",
      "type": "float",
      "doc": "Total observed versus predicted angular separation on the sky."
    },
    {
      "name": "ephOffsetRa",
      "type": "double",
      "doc": "Offset between observed and predicted position in the R.A. direction (includes cos(dec) term)."
    },
    {
      "name": "ephOffsetDec",
      "type": "double",
      "doc": "Offset between observed and predicted position in declination."
    },
    {
      "name": "ephOffsetAlongTrack",
      "type": "float",
      "doc": "Offset between observed and predicted position in the along-track direction on the sky."
    },
    {
      "name": "ephOffsetCrossTrack",
      "type": "float",
      "doc": "Offset between observed and predicted position in the cross-track direction on the sky."
    },
    {
      "name": "helio_x",
      "type": "float",
      "doc": "Cartesian heliocentric X coordinate at light-emission time (ICRS)."
    },
    {
      "name": "helio_y",
      "type": "float",
      "doc": "Cartesian heliocentric Y coordinate at light-emission time (ICRS)."
    },
    {
      "name": "helio_z",
      "type": "float",
      "doc": "Cartesian heliocentric Z coordinate at light-emission time (ICRS)."
    },
    {
      "name": "helio_vx",
      "type": "float",
      "doc": "Cartesian heliocentric X velocity at light-emission time (ICRS)."
    },
    {
      "name": "helio_vy",
      "type": "float",
      "doc": "Cartesian heliocentric Y velocity at light-emission time (ICRS)."
    },
    {
      "name": "helio_vz",
      "type": "float",
      "doc": "Cartesian heliocentric Z velocity at light-emission time (ICRS)."
    },
    {
      "name": "helio_vtot",
      "type": "float",
      "doc": "The magnitude of the heliocentric velocity vector, sqrt(vx*vx + vy*vy + vz*vz)."
    },
    {
      "name": "topo_x",
      "type": "float",
      "doc": "Cartesian topocentric X coordinate at light-emission time (ICRS)."
    },
    {
      "name": "topo_y",
      "type": "float",
      "doc": "Cartesian topocentric Y coordinate at light-emission time (ICRS)."
    },
    {
      "name": "topo_z",
      "type": "float",
      "doc": "Cartesian topocentric Z coordinate at light-emission time (ICRS)."
    },
    {
      "name": "topo_vx",
      "type": "float",
      "doc": "Cartesian topocentric X velocity at light-emission time (ICRS)."
    },
    {
      "name": "topo_vy",
      "type": "float",
      "doc": "Cartesian topocentric Y velocity at light-emission time (ICRS)."
    },
    {
      "name": "topo_vz",
      "type": "float",
      "doc": "Cartesian topocentric Z velocity at light-emission time (ICRS)."
    },
    {
      "name": "topo_vtot",
      "type": "float",
      "doc": "The magnitude of the topocentric velocity vector, sqrt(vx*vx + vy*vy + vz*vz)."
    },
    {
      "name": "diaDistanceRank",
      "type": "int",
      "doc": "The rank of the diaSourceId-identified source in terms of its closeness to the predicted SSO position.  If diaSourceId is the nearest DiaSource to this SSO prediction, diaSourceDistanceRank=1 would be set. If it is the second nearest, it would be 2, etc."
    }
  ]
}