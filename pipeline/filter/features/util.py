import json
import math
#These colour corrections are multiplied by the extinction E(B-V) to get a magnitude correction. 
#They are from Table 6 of Schlafly and Finkbeiner with RV=3.1
#https://iopscience.iop.org/article/10.1088/0004-637X/737/2/103
EXTCOEF   = {'u':4.145, 'g':3.237, 'r':2.273, 'i':1.684, 'z':1.323, 'y':1.088}

def getECFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources
    sources = sorted(alert['diaSourcesList'], 
        key=lambda source: source['midpointMjdTai'])
    sources = [s for s in sources if s['psfFlux'] is not None]
    flux = []
    time = []
    band = []
    for s in sources:
        flux.append(s['psfFlux']*math.pow(10, alert['ebv']*EXTCOEF[s['band']]/2.5))
        time.append(s['midpointMjdTai'])
        band.append(s['band'])
    return (flux, time, band)

def getFluxTimeBand(alert):
    # gets the flux,time for all non null fluxes in diaSources
    sources = sorted(alert['diaSourcesList'], 
        key=lambda source: source['midpointMjdTai'])
    sources = [s for s in sources if s['psfFlux'] is not None]
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
