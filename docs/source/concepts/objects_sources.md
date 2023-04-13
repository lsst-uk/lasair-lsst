# Objects and Sources

Lasair deals in *objects* and *sources*. A source is a detection by the telescope of an object. 
A source is a collection of pixels on the telecsopes light-collection device, which is significantly
brighter than it was in the reference imagery, that was taken at the beginning of the survey. 
A source is detected with a specific [narrowband optical filter](https://en.wikipedia.org/wiki/Photometric_system):
LSST uses filters u,g,r,i,z and ZTF uses g,r.

When a lot of sources are found in the same place in the sky, the collection is called an object. 
Thus an object is a star or similar that *does not move* in the sky. 
Usually it is assumed that an object corresponds to a real astrophysical object, such as star or
something extragalactic.

The brightness of a source in a transient survey is actually a *difference* brightness.
If an object is a variable star, then its optical flux was measured before the survey -- 
a reference flux -- and the source detections is the difference, positive or negative, from this.
When brightness is expressed as magnitudes, this measurement has two parts: absolute value, converted 
to magnitudes, and a flag to indicate positive or negative difference.

There are also solar-system objects and solar-system sources. The sources correspond to detections, 
and the objects to asteroids or other moving bodies in our solar system. However, the association 
of sources is mor difficult becuase that are in different positions in the sky due to orbital motion.
