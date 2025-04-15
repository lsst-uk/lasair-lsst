## Examples

### Finding tidal disruption events (TDE)

The beginning of a tidal disruption event begins with the first fuel being 
thrown at the black hole. The flux rises quickly, and is very hot, above 8000K.
The [NEEDLE project](https://academic.oup.com/mnras/article/531/2/2474/7685960) 
will search the LSST transient stream for such events, and the following
filter is a possible way to reduce the deluge of LSST alerts to something manageable.

#### Fast riser
We want objects with a rapid initial rise, and nothing there before. We can make SQL like this:
```
    mjdnow() - objects.lastDiaSourceMJD < 7   # must be diaSource in last 7 days
AND mjdnow() - objects.firstDiaSourceMJD < 30 # nothing before 30 days ago
AND objects.BBBRiseRate > 0.2                 # magnitudes per day
```
The first two lines are about epochs of first and last diaSources in this diaObject:
we want a recent brightening, and nothing there before
The last line refers to the `bazinBlackBody` parametric fit, and here we are requiring
not only that the parameter-fitting was successful, but also the rise rate is
rapid -- 2 mags in 10 days.

#### Blue
The LSST survey that Lasair reports makes many "paired" observation, meaning only 30 minutes 
apart. For most astrophysical lightcurves, this time is essentially zero, meaning that
these paired diaSources can be used for a colour measurement. There is a catch however,
because of the six filters of LSST, and the many combinations: u+g, u+r, g+r, r+i,  i+z,  z+y
(LSST Cadence doc [here](https://survey-strategy.lsst.io/baseline/wfd.html)). 
With the two-filter ZTF, it was easy to intuit temperature from "g-r" magnitude differences.
To simplify filter building, Lasair computes the equivalent temperature 
by fitting a blackbody profile to whichever pair generated the flux ratio.
We can use this to remove objects that are not very hot:
```
AND objects.latestPairColourTemp > 10          # temperature (kK) > 10,000 Kelvin
```
You could look for there being an earlier pair where it is **also** very hot:
```
AND objects.penultimatePairColourTemp > 10
```
#### Sherlock
Sherlock knows many catalogues, and compares them (crossmatch). 
Tidal Disruption events take place in the centres of galaxies, and we can look 
first at the catalogued galaxies.  At the simplest level, Sherlock reports 
these categories
- BS and VS (known bright star and known variable star), 
- AGN (known Active Galactic Nucleus), 
- CV (known cataclysmic variable), 
- SN and NT (in the skirts of / in the centre of a galaxy)

It is this latter pair that we use to find TDEs. 
We could also be more restrictive and just require the 'NT' classification.
Here is the SQL
```
AND sherlock_classifications.classification in ('SN', 'NT')
```
#### Absolute Magnitude
Lasair makes an estimate of peak absolute magnitude for anything that Sherlock
reports with a host galaxy -- that is SN and NT -- and therefore has a distance
measurement (z or photo-z). In this case, the lightcurve is corrected for extinction
and the highest flux selected, then converted to absolute magnitude.
```
AND peakExtCorrAbsMag < -19                  # peak extinction corrected absolute magnitude
```
#### Watchlist
A further cut for this type of alert might be a [publication of French and Zabludoff](https://ui.adsabs.harvard.edu/abs/2018ApJ...868...99F/abstract): 
Identifying Tidal Disruption Events via Prior Photometric Selection of Their Preferred Hosts.
The catalogue of 57,000 galaxies (is available from Vizier)[https://vizier.cds.unistra.fr/viz-bin/VizieR-3?-source=J/ApJ/868/99/table5], and there are (instructions)[core_functions/watchlists.html] 
for how to ingest this into Lasair.

In order to filter alerts based on a watchlist: in the filter builder web form, select 
the watchlist called "F+Z galaxy".

#### Bright enough 
If we are to request follow-up facility for this alert, it must be bright enough,
so that their spectrograph will have enough time to do the follow-up
There is a translation table and formula (here)[concepts.html#lightcurve], but 
this means brighter than magnitude 18.9 in either g or r filter:
```
AND (   objects.g_psfFlux > 100000               # 100000 nJ is mag 18.9
    OR  objects.g_psfFlux > 100000)
```
#### Finally
You can choose the SELECT part of the SQL query as you like, but the WHERE
section is where the filter is actually implemented. Here are the clauses from above
collected together for the WHERE section:
```
    mjdnow() - objects.lastDiaSourceMJD < 7   # must be diaSource in last 7 days
AND mjdnow() - objects.firstDiaSourceMJD < 30 # nothing before 30 days ago
AND objects.BBBRiseRate > 0.2                 # magnitudes per day
AND objects.latestPairColourTemp > 10  
AND objects.penultimatePairColourTemp > 10
AND sherlock_classifications.classification in ('SN', 'NT')
AND peakExtCorrAbsMag < -19  
```
with the watchlist **F+Z galaxies** chosen.





The idea of Lasair is that you build and share filters made from the sttributes listed in
[the schema browser]({%lasairurl%}/schema). The above sections give an idea of how ideas
can be converted to filters, and you should choose the sub-filters and parameters yourself.
