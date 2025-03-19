# This is the set of Lasair added features, together with those diaObject features 
# that we want as core attibutes.
# Those from Lasair have "origin": "lasair", and
# those copied from diaObject have "origin": "lsst"

schema = {
  "name": "objects",
  "fields": [

{"section":"Basic information", "doc":"ID, position, proper motion"},
{"name": "diaObjectId",        "type": "long",   "origin": "lsst",
    "doc": "ID for this object", "extra": "NOT NULL" },
{"name": "ra",                 "type": "double", "origin": "lsst",
    "doc": "Mean RA of this object" },
{"name": "decl",               "type": "double", "origin": "lsst",
    "doc": "Mean Dec of this object"},
{"name": "pmRa",               "type":"float",   "origin": "lsst",
    "doc":"Proper motion in right ascension (mas/yr)"},
{"name": "pmDec",              "type":"float",   "origin": "lsst",
    "doc":"Proper motion in declination (mas/yr)"},

{"section":"Lightcurve interval", "doc":"MJD of the first and last diaSource of this diaObject"},
{"name":  "lastDiaSourceMJD", "type": "double", "origin": "lasair",
    "doc": "Latest MJD of a diaSource" },
{"name": "firstDiaSourceMJD", "type": "double", "origin": "lasair",
    "doc": "Earliest MJD of a diaSource" },

{"section":"Latest Flux", "doc":"Most recent fluxes with errors"},
{"name":"u_psfFlux", "type":"float", "origin": "lasair",
    "doc":"Latest u flux (nJy)"},
{"name":"u_psfFluxMean", "type":"float", "origin": "lsst",
    "doc":"Weighted mean point-source model magnitude for u filter. (nJy)"},
{"name":"u_psfFluxMeanErr", "type":"float", "origin": "lsst",
    "doc":"Standard error of u_psfFluxMean. (nJy)"},

{"name":"g_psfFlux", "type":"float", "origin": "lasair",
    "doc":"Latest g flux (nJy)"},
{"name":"g_psfFluxMean", "type":"float", "origin": "lsst",
    "doc":"Weighted mean point-source model magnitude for g filter. (nJy)"},
{"name":"g_psfFluxMeanErr", "type":"float", "origin": "lsst",
    "doc":"Standard error of g_psfFluxMean. (nJy)"},

{"name":"r_psfFlux", "type":"float", "origin": "lasair",
    "doc":"Latest r flux (nJy)"},
{"name":"r_psfFluxMean", "type":"float", "origin": "lsst",
    "doc":"Weighted mean point-source model magnitude for r filter. (nJy)"},
{"name":"r_psfFluxMeanErr", "type":"float", "origin": "lsst",
    "doc":"Standard error of r_psfFluxMean. (nJy)"},

{"name":"i_psfFlux", "type":"float", "origin": "lasair",
    "doc":"Latest i flux (nJy)"},
{"name":"i_psfFluxMean", "type":"float", "origin": "lsst",
    "doc":"Weighted mean point-source model magnitude for i filter. (nJy)"},
{"name":"i_psfFluxMeanErr", "type":"float", "origin": "lsst",
    "doc":"Standard error of i_psfFluxMean. (nJy)"},

{"name":"z_psfFlux", "type":"float", "origin": "lasair",
        "doc":"Latest z flux (nJy)"},
{"name":"z_psfFluxMean", "type":"float", "origin": "lsst",
        "doc":"Weighted mean point-source model magnitude for z filter. (nJy)"},
{"name":"z_psfFluxMeanErr", "type":"float", "origin": "lsst",
        "doc":"Standard error of z_psfFluxMean. (nJy)"},

{"name":"y_psfFlux", "type":"float", "origin": "lasair",
        "doc":"Latest y flux (nJy)"},
{"name":"y_psfFluxMean", "type":"float", "origin": "lsst",
        "doc":"Weighted mean point-source model magnitude for y filter. (nJy)"},
{"name":"y_psfFluxMeanErr", "type":"float", "origin": "lsst",
        "doc":"Standard error of y_psfFluxMean. (nJy)"},

{"section":"Counting", "doc":"Counts of diaSources of different bands"},
    {"name": "nSources",  "type": "int", "origin": "lasair",
            "doc": "Number of diaSources associated with this diaObject", "extra": "NOT NULL"},
    {"name": "nuSources", "type": "int", "origin": "lasair",
            "doc": "Number of u sources" },
    {"name": "ngSources", "type": "int", "origin": "lasair",
            "doc": "Number of g sources" },
    {"name": "nrSources", "type": "int", "origin": "lasair",
            "doc": "Number of r sources" },
    {"name": "niSources", "type": "int", "origin": "lasair",
            "doc": "Number of i sources" },
    {"name": "nzSources", "type": "int", "origin": "lasair",
            "doc": "Number of z sources" },
    {"name": "nySources", "type": "int", "origin": "lasair",
            "doc": "Number of y sources" },

{"section":"Other/Nearest objects", "doc":"Other/Nearest objects from LSST and other catalogs"},
    {"name": "tns_name",          "type":"string",   "origin": "lasair",
            "doc":"TNS name of this object if it exists"},
    {"name": "nearbyObj1",        "type":"long",    "origin": "lsst",
            "doc":"Id of the closest nearby object."},
    {"name": "nearbyObj1Dist",    "type":"float",   "origin": "lsst",
            "doc":"Distance to nearbyObj1 (arcsec)"},
    {"name": "nearbyObj1LnP",     "type":"float",   "origin": "lsst",
            "doc":"Natural log of the probability that the observed diaObject is the same as the nearbyObj1."},

{"section":"Absolute magnitude", "doc":"Brightness at 1 parsec"},
{"name": "absMag",    "type": "float", "origin": "lasair",
        "doc":"Peak absolute magnitude (extinction corrected) if host galaxy with distance available"},
{"name": "absMagMJD", "type": "float", "origin": "lasair",
        "doc":"Peak absolute magnitude time if host galaxy with distance available"},

# https://roywilliams.github.io/papers/Bazin_Exp_Blackbody.pdf
{"section":"BazinBlackBody (BBB)", "doc":"Lightcurve fit as Bazin or Exp in time, Blackbody in wavelength"},
{"name": "BBBRiseRate",  "type": "float", "origin": "lasair",
        "doc": "Fitted Bazin or Exp rise rate" },
{"name": "BBBFallRate",  "type": "float", "origin": "lasair",
        "doc": "Fitted Bazin fall rate or NULL if Exp" },
{"name": "BBBTemp",      "type": "float", "origin": "lasair",
        "doc": "Fitted Bazin temperature, (kiloKelvins)" },
{"name": "BBBPeakFlux",  "type": "float", "origin": "lasair",
        "doc": "If Bazin fit, the peak flux (nJy)" },
{"name": "BBBPeakMJD",   "type": "float", "origin": "lasair",
        "doc": "If Bazin fit, the time of the peak brightness" },
{"name": "BBBPeakAbsMag","type": "float", "origin": "lasair",
        "doc": "If Bazin fit and Sherlock host with distance, the peak absolute magnitude" },

{"section":"Milky Way", "doc":"Galactic latitude and extinction"},
{"name": "glat", "type": "float", "origin": "lasair",
        "doc": "Galactic latitude" },
{"name": "ebv", "type": "float", "origin": "lasair",
        "doc": "Extinction E(B-V) Schlegel, Finkbeiner & Davis (1998)" },

# Student t-test for change of mean brightness
{"section":"Jump detector", "doc":"Number of sigma jump from 20 day mean"},
{"name": "jump1", "type": "float", "origin": "lasair",
        "doc": "Largest sigma jump of recent flux from previous -70 to -10  days"},
{"name": "jump2", "type": "float", "origin": "lasair",
        "doc": "Largest sigma jump of recent flux in different band from previous -70 to -10  days"},

{"section":"Pair colours", "doc":"Colours from 33-minute paired diaSources"},
{"name": "latestPairMJD",        "type": "float", "origin": "lasair",
        "doc": "Latest pair MJD" },
{"name": "latestPairColourMag",  "type": "float", "origin": "lasair",
        "doc": "Magnitude difference from latest pair" },
{"name": "latestPairColourBands","type": "string","origin": "lasair",
        "doc": "Bands used for latest pair colour, eg g-r, u-r" },
{"name": "latestPairColourTemp", "type": "float", "origin": "lasair",
        "doc": "Extinction corrected effective temperature from latest pair, kiloKelvin" },
{"name": "penultimatePairMJD",        "type": "float", "origin": "lasair",
        "doc": "Penultimate pair MJD" },
{"name": "penultimatePairColourMag",  "type": "float", "origin": "lasair",
        "doc": "Magnitude difference from Penultimate pair" },
{"name": "penultimatePairColourBands","type": "string","origin": "lasair",
        "doc": "Bands used for penultimate pair colour, eg g-r, u-r" },
{"name": "penultimatePairColourTemp","type": "float", "origin": "lasair",
        "doc": "Extinction corrected effective temperature from penultimate pair, kiloKelvin" },

{"section":"Utility", "doc":"Other attributes"},
# HTM index
{"name": "htm16", "type": "long", "origin": "lasair",
        "doc": "Hierarchical Triangular Mesh level 16", "extra": "NOT NULL" },
# timestamp for last modified
{"name": "timestamp",
    "type": "timestamp",
    "extra": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "origin": "lasair",
    "doc": "Time at which this object last modified",
},
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
