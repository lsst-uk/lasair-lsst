# Lightcurve

A lightcurve is a record of the brightness of an astrophysical object with time, so it is a collection of (time, brightness) pairs. For LSST the brightness of sources are calibrated and provided in flux, in the units of nanoJanskies (nJ). In ZTF the brightness measurement is provided as an AB magnitude.Note that the values in the lightcurve are *difference* fluxes, as defined in [Objects and Sources](objects_sources.html).

Since each source brightness is measured for a specific optical filter, there may be several lightcurves for a given object, for example the g-lightcurve and r-lightcurve will be derived from the detections in the g filter and r filter respectively.

When a source is detected at a significance of 5-sigma or more in the difference image then an alert is issued. This is defined as 5-sigma above the noise in the difference image, within a point-spread-function (PSF) aperture. 
This is the "unforced" photometry plotted in the object pages. Another important measurement computed from
the difference image is called the "forced" photometry. After an object has been identified then a photometric measurement (based on a PSF model) is forced at the position of the object on all images, irrespective of whether or not the object exists at 5-sigma significance. What is being measured is a "difference" in flux compared to the reference image. This flux can be positive or negative and can be simply calibrated in a physical flux unit such as a
nanoJansky.  More information about forced photometry and ZTF can be found 
[here](https://arxiv.org/abs/2305.16279).

The nature of the lightcurve informs us of the underlying astrophysics. Variable stars can be characterised by the shape and periodicity of their lightcurves, and explosive transients such as supernovae can be distinguished by the rise and fall rates of their lightcurves.
