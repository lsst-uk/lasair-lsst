schema = {
  "name": "mma_area_hits",
  "version": "1.0",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "ZTF object identifier"
    },
    {
      "name": "mw_id",
      "type": "int",
      "doc": "MMA area identifier"
    },
    {
      "name": "event_id",
      "type": "bigstring",
      "doc": "MMA event name"
    },
    {
      "name": "delta_t",
      "type": "float",
      "doc": "First diaSource time - event time (days)"
    },
    {
      "name": "contour",
      "type": "float",
      "doc": "2D skymap prob contour (0 to 1, smallest is best)"
    },
    {
      "name": "dist_host",
      "type": "float",
      "doc": "Distance (Mpc) to host galaxy"
    },
    {
      "name": "probdens2",
      "type": "float",
      "doc": "2D probability density, RA/Dec skymap"
    },
    {
      "name": "params",
      "type": "JSON",
      "doc": "Parameters of the association"
    },
  ],
  "indexes": [
    "PRIMARY KEY (`diaObjectId`)",
    "KEY `mw_id_idx` (`mw_id`),"
    "UNIQUE KEY `diaObjectId_mw_id_idx` (`diaObjectId`,`mw_id`)"
  ]
}
