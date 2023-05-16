schema = {
  "name": "objects",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "extra": "NOT NULL"
    },
    {
      "name": "htm16",
      "type": "bigint",
      "doc": "Hierarchical Triangular Mesh level 16",
      "extra": "NOT NULL"
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
      "name": "taimax",
      "type": "double",
      "doc": "Latest MJD of a diaSource"
    },
    {
      "name": "taimin",
      "type": "double",
      "doc": "Earliest MJD of a diaSource"
    },
    {
      "name": "ncand",
      "type": "int",
      "doc": "Number of daiSource in light curve"
    },
    {
      "name": "ncand_7",
      "type": "int",
      "doc": "Number of diaSource in last 7 days"
    }
  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)",
    "KEY htmid16idx (htm16)",
    "KEY idxRadecTai (radecTai)"
  ]
}
