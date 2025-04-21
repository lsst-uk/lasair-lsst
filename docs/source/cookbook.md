## Lasair Cookbook
```eval_rst
.. toctree::
   :maxdepth: 2

   cookbook
```



---
### Porting from ZTF
For watchlists and watchmaps, the porting process should be simple. Use the ZTF website
to navigate to the resource, then do Export/Original Watchlist File, which you can import 
into a new resource on lasair-lsst.

But filters are more difficult, as the objects attributes, used in SQL clauses, 
have been rebuilt for LSST. First an example WHERE clause from Lasair-ZTF:
```
sherlock_classifications.classification = "AGN"
AND objects.ncand >= 1
AND objects.decmean < 10
AND objects.jdgmax > jdnow() - 7
AND (objects.rmag < 20.0 OR objects.gmag < 20.0)
AND ((objects.magrmax- objects.magrmin) > 0.5)
AND objects.dmdt_g >= 1.5
```
Changes needed for Lasair-LSST are:
* Change `ncand` to `nSources` (could also use `nuSources`, `ngSources`, `nrSources`, 
etc for the six bands)
* Change `decmean` to `decl`
* For the third line, aboout timing, change `jdgmax` to `g_latestMJD`, for the most
recent g-band detection. There is also the time of latest detection in any band, that is
`lastDiaSourceMJD`. Also notice that Lasair-LSST uses MJD instead of JD.

Magnitude 20 is about 50,000 nJ, see [here](concepts) for 
explanation and conversion table/formula. And the replacement of `rmag` is `r_psfFlux`.
Perhaps the line about maximum and minimum magnitude could be replaced with something 
about the standard deviation of the lightcurve, the `objects-ext.r_psfFluxSigma`

The last line is most difficult, there is no direct replacement for the 
ZTF attribute `dmdt_g`, which has always been problematic. If you want fast risers,
the `bazinBlackBody` set of attributes tries for a collective approach, taking the 
whole 6-band lightcurve and fitting both temperature on the spectral axis, 
and explosion models on the time axis. If the fit has converged, the attribute
`BBBRiseRate` might work, it is an e-folding rate $e^{kt}$ for flux 
(linear in magnitude), but can also be 
thought of as magnitudes per day, within a few percent. 
Perhaps we choose 0.2 magnitudes a day.

So the clause looks like:
```
sherlock_classifications.classification = "AGN"
AND objects.nSources >= 1
AND objects.decl < 10
AND objects.g_latestMJD > mjdnow() - 7
AND (objects.r_psfFlux > 50000 OR objects.g_psfFlux > 50000)
AND (objects-ext.r_psfFluxSigma > 10000)
AND objects.BBBRiseRate > 0.2
```

If you have a porting problem from ZTF to LSST filters, please use the
[Community Forum](https://community.lsst.org/c/support/support-lasair/55).
---

### Find a fast riser
See the cookbook entry 
[Finding tidal disruption events (TDE)](#finding-tidal-disruption-events--tde-) below,
and do the first step only.

---
### Find SNII from TNS
Suppose you want those objects reported to TNS (Transient Name Server) which also
have been assigned `tns_type` as "SN II".

In the SELECT part of the filter form, put in:
```
objects.diaObjectId, 
crossmatch_tns.tns_prefix, crossmatch_tns.tns_name, crossmatch_tns.type
```
and in the WHERE part of the filter, 
we put in the classificartion constraint and latest first, and order
the results latest first.
```
crossmatch_tns.type = "SN II"
ORDER BY jdmax DESC
```
##### Filtering on TNS status
In the example above, we are concentrating on those LSST objects that are associated
with TNS objects. But sometimes we make a selection on objects, and just want to know 
if each object is in TNS, or not. Not an exclusive filter (TNS only), it's a
column in the table (may or may not be in TNS).

In this case, you can use the special attribute `objects.tns_name`. If this is in your
SELECT clause, there will be a column with TNS name, or blank if none.

---
### Finding alerts from my favourite objects

If your science depends on a specific population, you can make a *watchlist*.
Click "watchlists" on the front page of Lasair.

You can check the community resources first, perhaps the watchlist has already been built.
Otherwise, make a file like
```
<RA> | <Dec> | <name> [|<radius>]
```
for example
```
003.4835000|-18.9018056|SHBL J001355.9-185406
008.3931667|-19.3591389|KUV 00311-1938
```
If your watchlist is in a catalogue hosted by Vizier, 
[there are instructions](core_functions/watchlists.html) how to make this file.

Then the file can be ingested using the Lasair web: Watchlists/Create New.

Then make a filter based on the watchlist:
- Filter-builder web page: go to "Filters", then select your watchlist. 
- With the API
there is a notebook [Query objects coincident with a watchlist](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/Query_Watchlist.ipynb) that shows the steps.

When you Save the filter, you can enable streaming processing, so that you get alerts 
as soon as possible. Lasair supports email/batch and kafka, so thet your machine can 
get the filtered alert stream.
---
### Poking about in Gaia with ZTF
There is a lot of data available at [Lasair ZTF](https://lasair-ztf.lsst.ac.uk/), 
and not very much at [Lasair LSST](https://lasair-lsst.lsst.ac.uk/).
Let's look at the tools available in the 2-band ZTF object table, 
versus the object table of the 6-band LSST object table. In the former case, we can ask about 
each band separately, but for 6 bands we have tried to make features that give a 
comprehensive picture.

**Filtering Lasair-ZTF**

To illustrate,
lets see if we can find any outbursts amongst the Gaia catalogue of White Dwarfs.
There are a million of them in [GaiaWhiteDwarfsDR3](https://lasair-ztf.lsst.ac.uk/watchlists/1021/).
Let's start by looking at all alerts coincident with the watchlist 
(in Lasair: click Filters/Create New/Select watchlist/Run Filter/Save Filter). 
Already included in the sample filter is `objects.jdmax > jdnow()-365` which means 
there must have been a detection in the last year. So we can keep that.

Let's require a lightcurve with more than a few detections, say 10. For ZTF, we can utilise
the lightcurve shape attributes `dmdt_g` and `dmdt_r`. All you need for the SELECT is the `objectId`,
than you can click on the link to see the lightcurve.
The WHERE section is then:

```
objects.jdmax > jdnow()-365
and (objects.dmdt_g > 0.2 OR objects.dmdt_r > 0.2)
and objects.ncandgp > 10
```
Here are a few lightcurves I noticed.

- g-band brightess falling for 10 days while r brightness rising
[ZTF20acvedsk](https://lasair-ztf.lsst.ac.uk/objects/ZTF20acvedsk/)

- In the Gaia WD catalogue. Sherlock says CV. 
Long slow rise over a year then a fall over a year.
[ZTF18abvgcbb](https://lasair-ztf.lsst.ac.uk/objects/ZTF18abvgcbb/)

- Was fainter than it was at reference, brighter than references 2024-11-20
[ZTF17aaaikoz](https://lasair-ztf.lsst.ac.uk/objects/ZTF17aaaikoz/)

**Moving to LSST**

For the equivalent LSST filter, 
it would be perhaps g-flux compared to the mean.
More comprehensively, the 
Bazin-Black-Body (BBB) set of attibutes is an attempt to fit the 2D spectro-lightcurve 
with an explosive model (exponential in flux, linear in magnitude). 
That attribute would be `BBBRiseRate`, an e-folding rate, 
which is approximately the same as magnitudes per day.
The BBB also tries to fit a Bazin in the time direction 
-- exponential rise then exponential fall in flux.

Another way to do it is `jump1` or `jump2` which compare the latest diaSources, in all 6 bands,
with a baseline history between 70 and 10 days ago. The jump statistics are each number
of sigma for two wavebands. 



---
### Absolute magnitude
Under some circumstances, it is possible to estimate the intrinsic luminosity 
of an astrophysical object -- usually called the absolute magnitude. 
This estimate is only made if the Rubin object has a good chance of being 
associated with a galaxy whose distance is known. Below we combine flux, sky position, 
and redshift to estimate the peak absolute magnitude of a Rubin object.
Let $f_\nu$ be the flux in nanoJansky, and $\delta f$ its uncertainty.

Flux is related to $M_{AB}$, the observed magnitudes in the band of LSST.
See [Lasair Concepts](concepts.html?Lightcurve#lightcurve) for a conversion table.

$M_{AB}$ = 2.5 log $f_\nu$ + 8.9, for $f$ in Jy

$M_{AB}$ = 2.5 log $f_\nu$ + 31.4, for $f$ in nJy

$\delta M_{AB}$ = 1.08574 $\delta f/f$

Let $M_R$ be absolute magnitude in restframe band R. It is related to apparent magnitude, distance, extinction, and k-correction.

$M_R = M_{AB} - \mu + K_{RO} - A_O$

Here $\mu$ is the distance modulus, $K_{RO}$ is the k-correction to convert for wavelength shifting from band R to the band O. For redshift $z$, we have $K_{RO} = -2.5 log (1+z)$.

$A_O$ is extinction in observed band (foreground for magnitudes in the AB system, 
Therefore

$M_R = m_O - \mu - A_R + 2.5 log (1+z)$

We should also quote the rest frame wavelength this is the effective wavelength for $M_R$:

$\lambda_R = \lambda_O/(1+z)$

Error on $M_R$:
Sum the variances of the sources of error:

$(\delta M_R)^2 = (\delta M_O)^2 + (\delta \mu)^2 + (\delta K)^2$

Note that $\delta K$ will be small: $\delta K \approx {2.5 \over ln 10} ({\delta z \over 1+z})$
A Taylor expansion of the K correction term yields $\delta K \approx 1.08574 ({\delta z \over 1+z})$.

$\delta M$ will come from the uncertainty in redshift $\delta z$, 
presume there is a python function to give $\mu$ and $\delta\mu$
from $z$ and $\delta z$ for the cosmology of $H_0$ = 67 
and $\Omega_m=0.3, \Omega_n=0.7$.

---
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
    mjdnow() - objects.lastDiaSourceMJD < 7
AND mjdnow() - objects.firstDiaSourceMJD < 30
AND objects.BBBRiseRate > 0.2
AND objects.latestPairColourTemp > 10  
AND objects.penultimatePairColourTemp > 10
AND sherlock_classifications.classification in ('SN', 'NT')
AND peakExtCorrAbsMag < -19  
```
with the watchlist **F+Z galaxies** chosen.

The idea of Lasair is that you build and share filters made from the sttributes listed in
[the schema browser]({%lasairurl%}/schema). The above sections give an idea of how ideas
can be converted to filters, and you should choose the sub-filters and parameters yourself.

