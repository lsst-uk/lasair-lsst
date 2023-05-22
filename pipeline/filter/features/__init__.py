#    { "name": "diaObjectId", "type": "long", "extra": "NOT NULL" },
#    {
#      "name": "htm16",
#      "type": "bigint",
#      "doc": "Hierarchical Triangular Mesh level 16",
#      "extra": "NOT NULL"
#    },
#
#    { "name": "ra",       "type": "double", "doc": "Mean RA of this object" },
#    { "name": "decl",     "type": "double", "doc": "Mean Dec of this object"},
#    { "name": "radecTai", "type": "double", "doc": "MJD of latest detection" },
#
#
#    { "name": "uPSFluxMean", "type": "float", "doc": "Mean u flux in nJansky" },
#    { "name": "gPSFluxMean", "type": "float", "doc": "Mean g flux in nJansky" },
#    { "name": "rPSFluxMean", "type": "float", "doc": "Mean r flux in nJansky" },
#    { "name": "iPSFluxMean", "type": "float", "doc": "Mean i flux in nJansky" },
#    { "name": "zPSFluxMean", "type": "float", "doc": "Mean z flux in nJansky" },
#    { "name": "yPSFluxMean", "type": "float", "doc": "Mean y flux in nJansky" },
#
#    { "name": "taimax", "type": "double", "doc": "Latest MJD of a diaSource" },
#    { "name": "taimin", "type": "double", "doc": "Earliest MJD of a diaSource" },
#
#    { "name": "ncand",   "type": "int", "doc": "Number of daiSource in light curve" },
#    { "name": "ncand_7", "type": "int", "doc": "Number of diaSource in last 7 days" }

__all__ = [
  "FeatureInterface",
  "CopyFeature",
  "diaObjectId",
  "htm16",
  "ra",
  "decl",
  "radecTai",
  "uPSFluxMean",
  "gPSFluxMean",
  "rPSFluxMean",
  "iPSFluxMean",
  "zPSFluxMean",
  "yPSFluxMean",
  "taimax",
  "taimin",
  "ncand",
  "ncand_7"
]
