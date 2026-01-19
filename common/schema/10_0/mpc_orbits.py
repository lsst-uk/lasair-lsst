schema = {
  'indexes':['PRIMARY KEY ("designation")'],
  "name": "mpc_orbits",
  "fields": [
    {
      "name": "id",
      "type": "int",
      "doc": "Internal ID (generally not seen/used by the user)"
    },
    {
      "name": "designation",
      "type": "string",
      "doc": "The primary provisional designation in unpacked form (e.g. 2008 AB)."
    },
    {
      "name": "packed_primary_provisional_designation",
      "type": "string",
      "doc": "The primary provisional designation in packed form (e.g. K08A00B)"
    },
    {
      "name": "unpacked_primary_provisional_designation",
      "type": "string",
      "doc": "The primary provisional designation in unpacked form (e.g. 2008 AB)"
    },
    {
      "name": "mpc_orb_jsonb",
      "type": "string",
      "doc": "Details of the orbit solution in JSON form"
    },
    {
      "name": "created_at",
      "type": "long",
      "doc": "When this row was created"
    },
    {
      "name": "updated_at",
      "type": "long",
      "doc": "When this row was updated"
    },
    {
      "name": "orbit_type_int",
      "type": "int",
      "doc": "Orbit Type (Integer)"
    },
    {
      "name": "u_param",
      "type": "int",
      "doc": "U parameter"
    },
    {
      "name": "nopp",
      "type": "int",
      "doc": "number of oppositions"
    },
    {
      "name": "arc_length_total",
      "type": "double",
      "doc": "Arc length over total observations [days]"
    },
    {
      "name": "arc_length_sel",
      "type": "double",
      "doc": "Arc length over total observations *selected* [days]"
    },
    {
      "name": "nobs_total",
      "type": "int",
      "doc": "Total number of all observations (optical + radar) available"
    },
    {
      "name": "nobs_total_sel",
      "type": "int",
      "doc": "Total number of all observations (optical + radar) selected for use in orbit fitting"
    },
    {
      "name": "a",
      "type": "double",
      "doc": "Semi Major Axis [au]"
    },
    {
      "name": "q",
      "type": "double",
      "doc": "Pericenter Distance [au]"
    },
    {
      "name": "e",
      "type": "double",
      "doc": "Eccentricity"
    },
    {
      "name": "i",
      "type": "double",
      "doc": "Inclination [degrees]"
    },
    {
      "name": "node",
      "type": "double",
      "doc": "Longitude of Ascending Node [degrees]"
    },
    {
      "name": "argperi",
      "type": "double",
      "doc": "Argument of Pericenter [degrees]"
    },
    {
      "name": "peri_time",
      "type": "double",
      "doc": "Time from Pericenter Passage [days]"
    },
    {
      "name": "yarkovsky",
      "type": "double",
      "doc": "Yarkovsky Component [10^(-10)*au/day^2]"
    },
    {
      "name": "srp",
      "type": "double",
      "doc": "Solar-Radiation Pressure Component [m^2/ton]"
    },
    {
      "name": "a1",
      "type": "double",
      "doc": "A1 non-grav components [m^2/ton]"
    },
    {
      "name": "a2",
      "type": "double",
      "doc": "A2 non-grav components [m^2/ton]"
    },
    {
      "name": "a3",
      "type": "double",
      "doc": "A3 non-grav components [m^2/ton]"
    },
    {
      "name": "dt",
      "type": "double",
      "doc": "DT non-grav component"
    },
    {
      "name": "mean_anomaly",
      "type": "double",
      "doc": "Mean Anomaly [degrees]"
    },
    {
      "name": "period",
      "type": "double",
      "doc": "Orbital Period [days]"
    },
    {
      "name": "mean_motion",
      "type": "double",
      "doc": "Orbital Mean Motion [degrees per day]"
    },
    {
      "name": "a_unc",
      "type": "double",
      "doc": "Uncertainty on Semi Major Axis [au]"
    },
    {
      "name": "q_unc",
      "type": "double",
      "doc": "Uncertainty on Pericenter Distance [au]"
    },
    {
      "name": "e_unc",
      "type": "double",
      "doc": "Uncertainty on Eccentricity"
    },
    {
      "name": "i_unc",
      "type": "double",
      "doc": "Uncertainty on Inclination [degrees]"
    },
    {
      "name": "node_unc",
      "type": "double",
      "doc": "Uncertainty on Longitude of Ascending Node [degrees]"
    },
    {
      "name": "argperi_unc",
      "type": "double",
      "doc": "Uncertainty on Argument of Pericenter [degrees]"
    },
    {
      "name": "peri_time_unc",
      "type": "double",
      "doc": "Uncertainty on Time from Pericenter Passage [days]"
    },
    {
      "name": "yarkovsky_unc",
      "type": "double",
      "doc": "Uncertainty on Yarkovsky Component [10^(-10)*au/day^2]"
    },
    {
      "name": "srp_unc",
      "type": "double",
      "doc": "Uncertainty on Solar-Radiation Pressure Component [m^2/ton]"
    },
    {
      "name": "a1_unc",
      "type": "double",
      "doc": "Uncertainty on A1 non-grav components [m^2/ton]"
    },
    {
      "name": "a2_unc",
      "type": "double",
      "doc": "Uncertainty on A2 non-grav components [m^2/ton]"
    },
    {
      "name": "a3_unc",
      "type": "double",
      "doc": "Uncertainty on A3 non-grav components [m^2/ton]"
    },
    {
      "name": "dt_unc",
      "type": "double",
      "doc": "Uncertainty on DT non-grav component"
    },
    {
      "name": "mean_anomaly_unc",
      "type": "double",
      "doc": "Uncertainty on Mean Anomaly [degrees]"
    },
    {
      "name": "period_unc",
      "type": "double",
      "doc": "Uncertainty on Orbital Period [days]"
    },
    {
      "name": "mean_motion_unc",
      "type": "double",
      "doc": "Uncertainty on Orbital Mean Motion [degrees per day]"
    },
    {
      "name": "epoch_mjd",
      "type": "double",
      "doc": "Epoch of the Orbfit-Solution in MJD"
    },
    {
      "name": "h",
      "type": "double",
      "doc": "H-Magnitude"
    },
    {
      "name": "g",
      "type": "double",
      "doc": "G-Slope Parameter"
    },
    {
      "name": "not_normalized_rms",
      "type": "double",
      "doc": "unnormalized rms of the fit [arcsec]"
    },
    {
      "name": "normalized_rms",
      "type": "double",
      "doc": "rms of the fit [unitless]"
    },
    {
      "name": "earth_moid",
      "type": "double",
      "doc": "Minimum Orbit Intersection Distance [au] with respect to the Earths Orbit"
    },
    {
      "name": "fitting_datetime",
      "type": "long",
      "doc": "Date of the last orbit fit"
    }
  ]
}