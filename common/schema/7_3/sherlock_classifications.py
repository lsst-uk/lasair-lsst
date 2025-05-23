schema = {
  "name": "sherlock_classifications",
  "version": "1.0",
  "fields": [
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "ZTF object identifier, also known as transient_object_id"
    },
    {
      "name": "classification",
      "type": "string",
      "doc": "Top-ranked contextual classification for the transient (NULL, AGN, BS, CV, NT, ORPHAN, SN, UNCLEAR, VS)"
    },
    {
      "name": "association_type",
      "type": "string",
      "doc": "Association classification for the transient (NULL, AGN, BS, CV, NT, ORPHAN, SN, UNCLEAR, VS)"
    },
    {
      "name": "catalogue_table_name",
      "type": "bigstring",
      "doc": "Name/s of catalogue/s from which the best crossmatch is made"
    },
    {
      "name": "catalogue_object_id",
      "type": "bigstring",
      "doc": "Identifier in the catalogue/s from which the best crossmatch is made"
    },
    {
      "name": "catalogue_object_type",
      "type": "string",
      "doc": "Type of catalogue from which the best crossmatch is made"
    },
    {
      "name": "raDeg",
      "type": "double",
      "doc": "RA in degrees of the transient"
    },
    {
      "name": "decDeg",
      "type": "double",
      "doc": "Dec in degrees of the transient"
    },
    {
      "name": "separationArcsec",
      "type": "float",
      "doc": "Transient's angular separation (arcseconds) from the top-ranked catalogue source match"
    },
    {
      "name": "northSeparationArcsec",
      "type": "float",
      "doc": "Transient's angular separation (arcseconds) from the top-ranked catalogue source match"
    },
    {
      "name": "eastSeparationArcsec",
      "type": "float",
      "doc": "Transient's angular separation (arcseconds) from the top-ranked catalogue source match"
    },
    {
      "name": "physical_separation_kpc",
      "type": "float",
      "doc": "Distance in kilo parsec between transient and top-ranked catalogue source match"
    },
    {
      "name": "direct_distance",
      "type": "float",
      "doc": "Determined from a non-redshift related measurement - e.g. Cepheids/standard candle (Mpc)"
    },
    {
      "name": "distance",
      "type": "float",
      "doc": "Luminosity distance -- conversion from the spectral redshift (Mpc)"
    },
    {
      "name": "z",
      "type": "float",
      "doc": "Redshift of the top-ranked catalogue source match"
    },
    {
      "name": "photoZ",
      "type": "float",
      "doc": "Redshift of the top-ranked catalogue source match"
    },
    {
      "name": "photoZErr",
      "type": "float",
      "doc": "Redshift of the top-ranked catalogue source match"
    },
    {
      "name": "Mag",
      "type": "float",
      "doc": "Magnitude"
    },
    {
      "name": "MagFilter",
      "type": "string",
      "doc": "Magnitude filter"
    },
    {
      "name": "MagErr",
      "type": "float",
      "doc": "Magnitude error"
    },
    {
      "name": "classificationReliability",
      "type": "int",
      "doc": "Reliability of classification"
    },
    {
      "name": "major_axis_arcsec",
      "type": "float",
      "doc": "Size of associated galaxy in arcsec"
    },
    {
      "name": "annotator",
      "type": "bigstring",
      "doc": "Information about this annotation"
    },
    {
      "name": "additional_output",
      "type": "bigstring",
      "doc": "Addititonal information about this annotation"
    },
    {
      "name": "description",
      "type": "text",
      "doc": "Long-form, human-readable summary of the transient's characteristics as infered from Sherlock's classification"
    },
    {
      "name": "summary",
      "type": "bigstring",
      "doc": "Short-form summary of the transient's context usual for webpage quick-look summaries"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`diaObjectId`)"
  ]
}
