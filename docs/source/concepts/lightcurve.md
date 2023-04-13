# Lightcurve

A lightcurve is a record of the brightness of an astrophysical object with time, so it is a collection of 
(time, brightness) pairs. For LSST the brightness is measured as flux in nanoJanskies (nJ), and for ZTF it
is measured with the traditional magnitude system. Note that the values in the lightcurve are *difference*
fluxes, as defined in [Objects and Sources](objects_sources.html).

Since each source brightness is measured for a specific optical filter, there may be 
several lightcurves for a given object, for example the g-lightcurve and r-lightcurve will
be derived from the detections in the g filter and r filter respectively.

The nature of the lightcurve informs us of the underlying astrophysics. Variable stars can be characterised
by the shape of their lightcurves, and explosive transients such as supernovae can be distinguished by the 
rise and fall rates of their lightcurves.
