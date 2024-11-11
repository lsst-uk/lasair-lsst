schema = {
  "name": "ssObjects",
  "fields": [
    {
      "name": "ssObjectId",
      "type": "long"
    },
    {
      "name": "discoverySubmissionDate",
      "type": "double"
    },
    {
      "name": "firstObservationDate",
      "type": "double"
    },
    {
      "name": "arc",
      "type": "float"
    },
    {
      "name": "numObs",
      "type": "int"
    },
    {
      "name": "MOID",
      "type": "float"
    },
    {
      "name": "MOIDTrueAnomaly",
      "type": "float"
    },
    {
      "name": "MOIDEclipticLongitude",
      "type": "float"
    },
    {
      "name": "MOIDDeltaV",
      "type": "float"
    },
    {
      "name": "u_H",
      "type": "float"
    },
    {
      "name": "u_G12",
      "type": "float"
    },
    {
      "name": "u_HErr",
      "type": "float"
    },
    {
      "name": "u_G12Err",
      "type": "float"
    },
    {
      "name": "u_H_u_G12_Cov",
      "type": "float"
    },
    {
      "name": "u_Chi2",
      "type": "float"
    },
    {
      "name": "u_Ndata",
      "type": "int"
    },
    {
      "name": "g_H",
      "type": "float"
    },
    {
      "name": "g_G12",
      "type": "float"
    },
    {
      "name": "g_HErr",
      "type": "float"
    },
    {
      "name": "g_G12Err",
      "type": "float"
    },
    {
      "name": "g_H_g_G12_Cov",
      "type": "float"
    },
    {
      "name": "g_Chi2",
      "type": "float"
    },
    {
      "name": "g_Ndata",
      "type": "int"
    },
    {
      "name": "r_H",
      "type": "float"
    },
    {
      "name": "r_G12",
      "type": "float"
    },
    {
      "name": "r_HErr",
      "type": "float"
    },
    {
      "name": "r_G12Err",
      "type": "float"
    },
    {
      "name": "r_H_r_G12_Cov",
      "type": "float"
    },
    {
      "name": "r_Chi2",
      "type": "float"
    },
    {
      "name": "r_Ndata",
      "type": "int"
    },
    {
      "name": "i_H",
      "type": "float"
    },
    {
      "name": "i_G12",
      "type": "float"
    },
    {
      "name": "i_HErr",
      "type": "float"
    },
    {
      "name": "i_G12Err",
      "type": "float"
    },
    {
      "name": "i_H_i_G12_Cov",
      "type": "float"
    },
    {
      "name": "i_Chi2",
      "type": "float"
    },
    {
      "name": "i_Ndata",
      "type": "int"
    },
    {
      "name": "z_H",
      "type": "float"
    },
    {
      "name": "z_G12",
      "type": "float"
    },
    {
      "name": "z_HErr",
      "type": "float"
    },
    {
      "name": "z_G12Err",
      "type": "float"
    },
    {
      "name": "z_H_z_G12_Cov",
      "type": "float"
    },
    {
      "name": "z_Chi2",
      "type": "float"
    },
    {
      "name": "z_Ndata",
      "type": "int"
    },
    {
      "name": "y_H",
      "type": "float"
    },
    {
      "name": "y_G12",
      "type": "float"
    },
    {
      "name": "y_HErr",
      "type": "float"
    },
    {
      "name": "y_G12Err",
      "type": "float"
    },
    {
      "name": "y_H_y_G12_Cov",
      "type": "float"
    },
    {
      "name": "y_Chi2",
      "type": "float"
    },
    {
      "name": "y_Ndata",
      "type": "int"
    },
    {
      "name": "medianExtendedness",
      "type": "float"
    }
  ],
  "indexes": ['PRIMARY KEY ("ssObjectId")']
}
