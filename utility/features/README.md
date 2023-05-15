## Sample alerts, plots, and tests for LSST lightcurve features

Each alert consists of four JSON-encoded objects, three of which are lists
- `diaObject`
    - `diaObjectId`: ID for this object

List called `diaSourceList` of:
- `diaSource`: A detection of an object inb a given filter
    - `diaSourceId`: ID for this source
    - `midPointTai`: MJD of detection
    - `filterName`: one of u, g, r, i, z, y
    - `psFlux`: Flux in nano Janskies
    - `psFluxErr`: estimated error of flux

List called `diaForcedSourceList` of:
- `diaForcedSource`: A forced detection of an object inb a given filter
    - `diaSourceId`: ID for this source
    - `midPointTai`: MJD of detection
    - `filterName`: one of u, g, r, i, z, y
    - `psFlux`: Flux in nano Janskies
    - `psFluxErr`: estimated error of flux

List called diaNondetectionLimitsList of:
- `diaNondetectionLimits`
    - `midPointTai`: MJD of nondetection
    - `filterName`: one of u, g, r, i, z, y
    - `diaNoise`: upper limit of flux sensitivity

There are sample alerts to test the feature computing software. These come in **categories**:
Currently we have two categories of sample alerts:
- BazinBB: A Bazin curve in time, with a blackbody spectrum in wavelength
- sampleAlerts: Reduced from the [sample alerts](https://github.com/lsst-dm/sample_alert_info) released by Rubin.
