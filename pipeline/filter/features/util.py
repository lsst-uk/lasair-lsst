import json

def getFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources
    sources = sorted(alert['diaSourcesList'], 
        key=lambda source: source['midpointMjdTai'])
    sources = [s for s in sources if s['psfFlux'] is not None]
    flux = [s['psfFlux']        for s in sources]
    time = [s['midpointMjdTai'] for s in sources]
    band = [s['band']           for s in sources]
    return (flux, time, band)

def getMostFluxTimeBand(alert, nforced=4):
    # gets the flux,time for all non null fluxes in diaSources 
    # and most recent nforced from the forcedSourceOnDiaObjects
    sources = []
    forcedSources = sorted(alert['diaForcedSourcesList'], 
        key=lambda source: source['midpointMjdTai'])
    # get last nforced of the forced phot
    for f in forcedSources[-nforced:]:
        sources.append({
            'psfFlux'       : f['psfFlux'], 
            'midpointMjdTai': f['midpointMjdTai'],
            'band'          : f['band'],
        })
    sources += alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midpointMjdTai'])
    sources = [s for s in sources if s['psfFlux'] is not None]
#    print(json.dumps(sources, indent=2))   #############
    flux = [s['psfFlux']        for s in sources]
    time = [s['midpointMjdTai'] for s in sources]
    band = [s['band']           for s in sources]
    return (flux, time, band)

def getAllFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources and forcedSourceOnDiaObjects
    sources = []
    for f in alert['diaForcedSourcesList']:
        sources.append({
            'psfFlux'       : f['psfFlux'], 
            'midpointMjdTai': f['midpointMjdTai'],
            'band'          : f['band'],
        })
    sources += alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midpointMjdTai'])
    sources = [s for s in sources if s['psfFlux'] is not None]
#    print(json.dumps(sources, indent=2))   #############
    flux = [s['psfFlux']        for s in sources]
    time = [s['midpointMjdTai'] for s in sources]
    band = [s['band']           for s in sources]
    return (flux, time, band)
