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
      "name": "skyprob",
      "type": "float",
      "doc": "2D skymap prob contour (0 to 1, smallest is best)"
    },
    {
      "name": "distsigma",
      "type": "float",
      "doc": "number of std dev of alert from GW distance estimate"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`diaObjectId`)",
    "KEY `mw_id_idx` (`mw_id`),"
    "UNIQUE KEY `diaObjectId_mw_id_idx` (`diaObjectId`,`mw_id`)"
  ]
}
