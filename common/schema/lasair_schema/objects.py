schema = {
  "name": "objects",
  "fields": [

# These copied from the LSST diaObject
# https://sdm-schemas.lsst.io/apdb.html

{"section":"Basic information", "doc":"ID, position, proper motion"},
    {"name": "diaObjectId",        "type": "long",   "doc": "ID for this object", "extra": "NOT NULL" },
    {"name": "ra",                 "type": "double", "doc": "Mean RA of this object" },
    {"name": "decl",               "type": "double", "doc": "Mean Dec of this object"},
    {"name": "pmRa",               "type":"float",   "doc":"Proper motion in right ascension (mas/yr)"},
    {"name": "pmDec",              "type":"float",   "doc":"Proper motion in declination (mas/yr)"},

{"section":"Lightcurve interval", "doc":"MJD of the first and last diaSource of this diaObject"},
    {"name":  "lastDiaSourceMJD", "type": "double", "doc": "Latest MJD of a diaSource" },
    {"name": "firstDiaSourceMJD", "type": "double", "doc": "Earliest MJD of a diaSource" },

{"section":"Latest Flux", "doc":"Most recent fluxes with errors"},
{"name":"u_psfFlux", "type":"float", "doc":"Latest u flux (nJy)"},
{"name":"u_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for u filter. (nJy)"},
{"name":"u_psfFluxMeanErr", "type":"float", "doc":"Standard error of u_psfFluxMean. (nJy)"},

{"name":"g_psfFlux", "type":"float", "doc":"Latest g flux (nJy)"},
{"name":"g_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for g filter. (nJy)"},
{"name":"g_psfFluxMeanErr", "type":"float", "doc":"Standard error of g_psfFluxMean. (nJy)"},

{"name":"r_psfFlux", "type":"float", "doc":"Latest r flux (nJy)"},
{"name":"r_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for r filter. (nJy)"},
{"name":"r_psfFluxMeanErr", "type":"float", "doc":"Standard error of r_psfFluxMean. (nJy)"},

{"name":"i_psfFlux", "type":"float", "doc":"Latest i flux (nJy)"},
{"name":"i_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for i filter. (nJy)"},
{"name":"i_psfFluxMeanErr", "type":"float", "doc":"Standard error of i_psfFluxMean. (nJy)"},

{"name":"z_psfFlux", "type":"float", "doc":"Latest z flux (nJy)"},
{"name":"z_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for z filter. (nJy)"},
{"name":"z_psfFluxMeanErr", "type":"float", "doc":"Standard error of z_psfFluxMean. (nJy)"},

{"name":"y_psfFlux", "type":"float", "doc":"Latest y flux (nJy)"},
{"name":"y_psfFluxMean", "type":"float", "doc":"Weighted mean point-source model magnitude for y filter. (nJy)"},
{"name":"y_psfFluxMeanErr", "type":"float", "doc":"Standard error of y_psfFluxMean. (nJy)"},

{"section":"Counting", "doc":"Counts of diaSources of different bands"},
    {"name": "nSources",  "type": "int", "doc": "Number of diaSources associated with this diaObject", "extra": "NOT NULL"},
    {"name": "nuSources", "type": "int", "doc": "Number of u sources" },
    {"name": "ngSources", "type": "int", "doc": "Number of g sources" },
    {"name": "nrSources", "type": "int", "doc": "Number of r sources" },
    {"name": "niSources", "type": "int", "doc": "Number of i sources" },
    {"name": "nzSources", "type": "int", "doc": "Number of z sources" },
    {"name": "nySources", "type": "int", "doc": "Number of y sources" },

{"section":"Other/Nearest objects", "doc":"Other/Nearest objects from LSST and other catalogs"},
    {"name": "tns_name",          "type":"string",   "doc":"TNS name of this object if it exists"},
    {"name": "nearbyObj1",        "type":"long",     "doc":"Id of the closest nearby object."},
    {"name": "nearbyObj1Dist",    "type":"float",    "doc":"Distance to nearbyObj1 (arcsec)"},
    {"name": "nearbyObj1LnP",     "type":"float",    "doc":"Natural log of the probability that the observed diaObject is the same as the nearbyObj1."},

{"section":"Absolute magnitude", "doc":"Brightness at 1 parsec"},
    {"name": "absMag", "type": "float", "doc":"Brightest peak absolute magnitude if host galaxy with distance available"},

# https://roywilliams.github.io/papers/Bazin_Exp_Blackbody.pdf
{"section":"BazinBlackBody (BBB)", "doc":"Lightcurve fit as Bazin or Exp in time, Blackbody in wavelength"},
    {"name": "BBBRiseRate", "type": "float", "doc": "Fitted Bazin or Exp rise rate" },
    {"name": "BBBFallRate", "type": "float", "doc": "Fitted Bazin fall rate or NULL if Exp" },
    {"name": "BBBTemp",     "type": "float", "doc": "Fitted Bazin temperature, kiloKelvins" },

{"section":"Milky Way", "doc":"Galactic latitude and extinction"},
    {"name": "glat", "type": "float", "doc": "Galactic latitude" },
    {"name": "ebv", "type": "float", "doc": "Extinction E(B-V) Schlegel, Finkbeiner & Davis (1998)" },

# Student t-test for change of mean brightness
{"section":"Jump detector", "doc":"Number of sigma jump from 20 day mean"},
    {"name": "jumpFromMean20", "type": "float", "doc": "Number of sigma jump of recent flux from previous 20 days"},

{"section":"Revisit colours", "doc":"Colours from 33-minute revisits"},
    {"name": "latest_rv_mjd",         "type": "float", "doc": "Latest revisit MJD" },
    {"name": "latest_rv_colour_mag",  "type": "float", "doc": "Magnitude difference from latest revisit" },
    {"name": "latest_rv_colour_bands","type": "string",   "doc": "Bands used for latest revisit colour, eg g-r, u-r" },
    {"name": "latest_rv_colour_temp", "type": "float", "doc": "Effective temperature from latest revisit, kiloKelvin" },
    {"name": "penultimate_rv_mjd",         "type": "float", "doc": "Penultimate revisit MJD" },
    {"name": "penultimate_rv_colour_mag",  "type": "float", "doc": "Magnitude difference from Penultimate revisit" },
    {"name": "penultimate_rv_colour_bands","type": "string",   "doc": "Bands used for penultimate revisit colour, eg g-r, u-r" },
    {"name": "penultimate_rv_colour_temp", "type": "float", "doc": "Effective temperature from penultimate revisit, kiloKelvin" },

{"section":"Utility", "doc":"Other attributes"},
# HTM index
    {"name": "htm16", "type": "long", "doc": "Hierarchical Triangular Mesh level 16", "extra": "NOT NULL" },
# timestamp for last modified
    {"name": "timestamp",
      "type": "timestamp",
      "extra": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
      "doc": "Time at which this object last modified"
    },
  ],
  "ext_fields": [
#    { "name": "diaObjectId", "type": "long", "doc": "Unique identifier of this DiaObject." },
#    { "name": "ra", "type": "double", "doc": "Right ascension coordinate of the position of the object at time radecMjdTai." },
    { "name": "raErr", "type": "float", "doc": "Uncertainty of ra." },
#    { "name": "decl", "type": "double", "doc": "Declination coordinate of the position of the object at time radecMjdTai." },
    { "name": "decErr", "type": "float", "doc": "Uncertainty of dec." },
    { "name": "ra_dec_Cov", "type": "float", "doc": "Covariance between ra and dec." },
    { "name": "radecMjdTai", "type": "double", "doc": "Time at which the object was at a position ra/dec, expressed as Modified Julian Date, International Atomic Time." },
#    { "name": "pmRa", "type": "float", "doc": "Proper motion in right ascension." },
    { "name": "pmRaErr", "type": "float", "doc": "Uncertainty of pmRa." },
#    { "name": "pmDec", "type": "float", "doc": "Proper motion of declination." },
    { "name": "pmDecErr", "type": "float", "doc": "Uncertainty of pmDec." },
    { "name": "parallax", "type": "float", "doc": "Parallax." },
    { "name": "parallaxErr", "type": "float", "doc": "Uncertainty of parallax." },
    { "name": "pmRa_pmDec_Cov", "type": "float", "doc": "Covariance of pmRa and pmDec." },
    { "name": "pmRa_parallax_Cov", "type": "float", "doc": "Covariance of pmRa and parallax." },
    { "name": "pmDec_parallax_Cov", "type": "float", "doc": "Covariance of pmDec and parallax." },
    { "name": "pmParallaxLnL", "type": "float", "doc": "Natural log of the likelihood of the linear proper motion parallax fit." },
    { "name": "pmParallaxChi2", "type": "float", "doc": "Chi^2 static of the model fit." },
    { "name": "pmParallaxNdata", "type": "int", "doc": "The number of data points used to fit the model." },

#    { "name": "u_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for u filter." },
#    { "name": "u_psfFluxMeanErr", "type": "float", "doc": "Standard error of u_psfFluxMean." },
    { "name": "u_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of u_psfFlux." },
    { "name": "u_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of u_psfFlux around u_psfFluxMean." },
    { "name": "u_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute u_psfFluxChi2." },
    { "name": "u_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for u filter." },
    { "name": "u_fpFluxMeanErr", "type": "float", "doc": "Standard error of u_fpFluxMean." },
    { "name": "u_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of u_fpFlux." },
    { "name": "u_psfFluxErrMean", "type": "float", "doc": "Mean of the u band flux errors." },

#    { "name": "g_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for g filter." },
#    { "name": "g_psfFluxMeanErr", "type": "float", "doc": "Standard error of g_psfFluxMean." },
    { "name": "g_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of g_psfFlux." },
    { "name": "g_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of g_psfFlux around g_psfFluxMean." },
    { "name": "g_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute g_psfFluxChi2." },
    { "name": "g_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for g filter." },
    { "name": "g_fpFluxMeanErr", "type": "float", "doc": "Standard error of g_fpFluxMean." },
    { "name": "g_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of g_fpFlux." },
    { "name": "g_psfFluxErrMean", "type": "float", "doc": "Mean of the g band flux errors." },
    
#    { "name": "r_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for r filter." },
#    { "name": "r_psfFluxMeanErr", "type": "float", "doc": "Standard error of r_psfFluxMean." },
    { "name": "r_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of r_psfFlux." },
    { "name": "r_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of r_psfFlux around r_psfFluxMean." },
    { "name": "r_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute r_psfFluxChi2." },
    { "name": "r_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for r filter." },
    { "name": "r_fpFluxMeanErr", "type": "float", "doc": "Standard error of r_fpFluxMean." },
    { "name": "r_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of r_fpFlux." },
    { "name": "r_psfFluxErrMean", "type": "float", "doc": "Mean of the r band flux errors." },

#    { "name": "i_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for i filter." },
#    { "name": "i_psfFluxMeanErr", "type": "float", "doc": "Standard error of i_psfFluxMean." },
    { "name": "i_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of i_psfFlux." },
    { "name": "i_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of i_psfFlux around i_psfFluxMean." },
    { "name": "i_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute i_psfFluxChi2." },
    { "name": "i_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for i filter." },
    { "name": "i_fpFluxMeanErr", "type": "float", "doc": "Standard error of i_fpFluxMean." },
    { "name": "i_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of i_fpFlux." },
    { "name": "i_psfFluxErrMean", "type": "float", "doc": "Mean of the i band flux errors." },

#    { "name": "z_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for z filter." },
#    { "name": "z_psfFluxMeanErr", "type": "float", "doc": "Standard error of z_psfFluxMean." },
    { "name": "z_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of z_psfFlux." },
    { "name": "z_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of z_psfFlux around z_psfFluxMean." },
    { "name": "z_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute z_psfFluxChi2." },
    { "name": "z_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for z filter." },
    { "name": "z_fpFluxMeanErr", "type": "float", "doc": "Standard error of z_fpFluxMean." },
    { "name": "z_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of z_fpFlux." },
    { "name": "z_psfFluxErrMean", "type": "float", "doc": "Mean of the z band flux errors." },

#    { "name": "y_psfFluxMean", "type": "float", "doc": "Weighted mean point-source model magnitude for y filter." },
#    { "name": "y_psfFluxMeanErr", "type": "float", "doc": "Standard error of y_psfFluxMean." },
    { "name": "y_psfFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of y_psfFlux." },
    { "name": "y_psfFluxChi2", "type": "float", "doc": "Chi^2 statistic for the scatter of y_psfFlux around y_psfFluxMean." },
    { "name": "y_psfFluxNdata", "type": "int", "doc": "The number of data points used to compute y_psfFluxChi2." },
    { "name": "y_fpFluxMean", "type": "float", "doc": "Weighted mean forced photometry flux for y filter." },
    { "name": "y_fpFluxMeanErr", "type": "float", "doc": "Standard error of y_fpFluxMean." },
    { "name": "y_fpFluxSigma", "type": "float", "doc": "Standard deviation of the distribution of y_fpFlux." },
    { "name": "y_psfFluxErrMean", "type": "float", "doc": "Mean of the y band flux errors." },

#    { "name": "nearbyObj1", "type": "long", "doc": "Id of the closest nearby object." },
#    { "name": "nearbyObj1Dist", "type": "float", "doc": "Distance to nearbyObj1." },
#    { "name": "nearbyObj1LnP", "type": "float", "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj1." },
    { "name": "nearbyObj2", "type": "long", "doc": "Id of the second-closest nearby object." },
    { "name": "nearbyObj2Dist", "type": "float", "doc": "Distance to nearbyObj2." },
    { "name": "nearbyObj2LnP", "type": "float", "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj2." },
    { "name": "nearbyObj3", "type": "long", "doc": "Id of the third-closest nearby object." },
    { "name": "nearbyObj3Dist", "type": "float", "doc": "Distance to nearbyObj3." },
    { "name": "nearbyObj3LnP", "type": "float", "doc": "Natural log of the probability that the observed diaObject is the same as the nearbyObj3." },

  ],
  "indexes": [
    "PRIMARY KEY (diaObjectId)",
    "KEY htmid16idx (htm16)",
    "KEY idxMaxTai (lastDiaSourceMJD)"
  ]
}
if __name__ == "__main__":
    print('<h2>Fields of the Lasair Object Schema</h2>')
    print('<h3>Core Attributes</h3>')
    print('<table border=1>')
    for f in schema['fields']:
        if 'section' in f:
            print('</table>')
            print('<p><b>%s</b>: %s' % (f['section'], f['doc']))
            print('<table border=1>')
        elif 'name' in f:
            print('<tr><td><tt>%s</tt></td><td>%s</td>' % (f['name'], f['doc']))
    print('</table>')

    print('<h3>Extended Attributes</h3><table>')
    print('<table border=1>')
    for f in schema['ext_fields']:
       if 'name' in f:
            print('<tr><td><tt>%s</tt></td><td>%s</td>' % (f['name'], f['doc']))
    print('</table>')
