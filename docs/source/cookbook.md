## Lasair Cookbook
```eval_rst
.. toctree::
   :maxdepth: 2

   cookbook
```

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
we put in the classification constraint and latest first, and order
the results latest first.
```
crossmatch_tns.type = "SN II"
ORDER BY lastDiaSourceMjdTai DESC
```

You can select on multiple TNS types with this syntax:
```
crossmatch_tns.type in ["SN II", "AGN"]
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

Flux is related to the apparent magnitude ($m_{AB}$ measured in the observer frame band O.
See [Lasair Concepts](concepts.html?Lightcurve#lightcurve) for a conversion table.

$m_{AB}$ = -2.5 log $f_\nu$ + 8.9, for $f$ in Jy

$m_{AB}$ = -2.5 log $f_\nu$ + 31.4, for $f$ in nJy

Let $M_R$ be absolute magnitude in restframe band R. It is related to apparent magnitude, 
distance, extinction, and k-correction.

$M_R = m_{AB} - \mu - A_O + K_{RO}$

Here $\mu$ is the distance modulus, and
$A_O$ is extinction in observed band for magnitudes in the AB system.
Note that the foreground extinction we apply is for the Milky Way, 
so this is applied to the observer frame flux and magnitude measurement.

$K_{RO}$ is the k-correction to convert for wavelength shifting from band R to the band O. 
An accurate K-correction requires knowledge of the input spectrum and the redshift, 
along with the filter throughput function to calculate synthetic photometry. 
A user may want to do this for full scientific analysis but since 
Lasair filters are designed for rapid selection we provide the 
approximate k-correction only (e.g. as described in 
[Hogg et al. 2002](https://arxiv.org/abs/astro-ph/0210394)).
For redshift $z$, we have $K_{RO} = -2.5 log (1+z)$.  Therefore:

$M_R = m_O - \mu - A_O + 2.5 log (1+z)$

Note that the rest frame wavelength is shifted: the effective 
wavelength for $M_R$ is:

$\lambda_R = \lambda_O/(1+z)$

We can compute distance modulus $\mu$ from redshift $z$ following Ned Wright's
[cosmology calculator](https://www.astro.ucla.edu/~wright/cosmo_02.htm#DL).
For the code that computes absolute magnitude, see the 
[milky way notebook](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/4_milky_way.ipynb).

Error on $M_R$:
Sum the variances of the sources of error:

$(\delta M_R)^2 = (\delta M_O)^2 + (\delta \mu)^2 + (\delta K)^2$

The error of magnitude comes from the error in flux:
$\delta M_{AB}$ = 1.08574 $\delta f/f$

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
    mjdnow() - objects.lastDiaSourceMjdTai < 7   # must be diaSource in last 7 days
AND mjdnow() - objects.firstDiaSourceMjdTai < 30 # nothing before 30 days ago
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
The catalogue of 57,000 galaxies [is available from Vizier](https://vizier.cds.unistra.fr/viz-bin/VizieR-3?-source=J/ApJ/868/99/table5), and there are (instructions)[core_functions/watchlists.html] 
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
    mjdnow() - objects.lastDiaSourceMjdTai < 7
AND mjdnow() - objects.firstDiaSourceMjdTai < 30
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

