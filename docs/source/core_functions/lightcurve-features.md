# Lasair's Lightcurve Features

These are lightcurve and contextual features that can be used in Lasair filters.
For more information see [Schema Browser]({%lasairurl%}/schema)

### Object table
- Position and proper motion: diaObjectId, RA and Dec, proper motion.

- Lightcurve interval: MJD of the first and last diaSource in the lightcurve.

- Latest and mean flux: For each of the six bands, the latest flux in nJ, and the mean and its standard deviation.

- diaSource counts: total number of diaSources in the lightcurve, and siz counts for the number of sources of each band.

- Nearest objects: Name from TNS, if any, and nearest LSST object.

- Absolute magnitude: peak extincton corrected absolute magnitud, and the MJD of that peak.
See [Absolute Magnitude](cookbook.html#absolute-magnitude) in the Cookbook.

- Bazin black body fitting: A two-dimensional fit with blackbody in the spectral dimension
and either exponential flux rise or Bazin model for flux.
See the [notebook](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/6_bazinBlackBody.ipynb) for more information.

- Milky way: Galactic latitude and E(B-V) extinction.

- Jump detection: Finds the number of sigma the latest detection is from a mean in the previous 70 days. 
See the [notebook](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/3_jumpFromMean.ipynb) for more information.

- Pair colours: Finds magnitude differences for pairs of diaSources; also fits a black body temperature to the two fluxes. 
For more information see the [notebook](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/5_pair.ipynb).

### Sherlock table
Intelligent crossmatch from lutiple catalogues.
For more information see the [notebook](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/2_sherlock.ipynb), or
[Sherlock writeup](core_functions/sherlock.html).

### TNS table
Lasair keeps an up-to-date clone of the TNS database of ~100,000 supernovar, FRBs and other transient phenomena. See 
[Schema Browser]({%lasairurl%}/schema), and the [TNS website](https://www.wis-tns.org/).

### Extended Object Table
The extended objecct attributes are all those copied from the LSST `diaObject` that Lasair feels might not be important,
but includes them anyway for users who know what they mean.
