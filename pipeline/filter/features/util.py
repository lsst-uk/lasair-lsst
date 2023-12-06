def getFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources
    sources = sorted(alert['diaSourcesList'], 
        key=lambda source: source['midPointTai'])
    sources = [s for s in sources if s['psFlux'] is not None]
    flux = [s['psFlux']      for s in sources]
    time = [s['midPointTai'] for s in sources]
    band = [s['filterName']  for s in sources]
    return (flux, time, band)

def getAllFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources and forcedSourceOnDiaObjects
    sources = []
    for f in alert['forcedSourceOnDiaObjectsList']:
        sources.append({
            'psFlux'     : f['psfDiffFlux'], 
            'midPointTai': f['midPointTai'],
            'filterName' : f['band'],
        })
    sources += alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midPointTai'])
    sources = [s for s in sources if s['psFlux'] is not None]
    flux = [s['psFlux']      for s in sources]
    time = [s['midPointTai'] for s in sources]
    band = [s['filterName']  for s in sources]
    return (flux, time, band)
