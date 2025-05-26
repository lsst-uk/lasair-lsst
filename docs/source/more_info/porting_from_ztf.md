## Porting from Lasair-ZTF

For several years, the Lasair system has been delivering alerts from the 
[Zwicky Transient Facility (ZTF) ](https://www.ztf.caltech.edu/). But Lasair-LSST is a 
new system, built from the lessons of the ZTF prototype.

#### Account
To use Lasair-LSST, you will need to register again, with username, password, and email.
Your account with Lasair-ZTF will not be copied over, and the API token from Lasair-ZTF
will not work for Lasair-LSST.

#### Watchlists and Watchmaps
For watchlists and watchmaps, the porting process should be simple. Use the ZTF website
to navigate to the resource, then do Export/Original Watchlist File, which you can import 
into a new resource on lasair-lsst.

#### Filters
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

Magnitude 20 is about 50,000 nJ, see [here](concepts.html#lightcurve) for 
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
