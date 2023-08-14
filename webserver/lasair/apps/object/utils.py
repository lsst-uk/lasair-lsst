"""
Using plotly to make two stacked plots of a lightcurve, one with flux 
the other magnitude. If a distance is provided (in Mpc), then absolute flux 
and absolute magnitude are shown on the right axes.
Different filters (ugrizy) have fifferent colors.
Three types of flux/mag have different symbols and sizes -- 
   diaSource, diaForcedSource, diaNondetectionLimit

A legend can be made like this
<p>
&nbsp;&nbsp;&nbsp;&nbsp;
<span style="color:#9900cc"> &#x2B24;</span> u &nbsp;&nbsp;
<span style="color:#3366ff"> &#x2B24;</span> g &nbsp;&nbsp;
<span style="color:#33cc33"> &#x2B24;</span> r &nbsp;&nbsp;
<span style="color:#ffcc00"> &#x2B24;</span> i &nbsp;&nbsp;
<span style="color:#ff0000"> &#x2B24;</span> z &nbsp;&nbsp;
<span style="color:#cc6600"> &#x2B24;</span> y &nbsp;&nbsp;
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from astropy.time import Time
import math

# globals
fig       = None    # the figure being plotted
nuLnuLsun = None    # flux multipler for nuLnu (see bottom of this file)
magAbs    = None    # magnitude addition for distance

# Colors for the various filterNames
filterColor = {
   "u": "#9900cc",
   "g": "#3366ff",
   "r": "#33cc33",
   "i": "#ffcc00",
   "z": "#ff0000",
   "y": "#cc6600",
}

def flux2mag(flux):
    # Compute magnitude from flux
    if flux > 0: return 31.4 - 2.5*math.log10(flux)
    else:        return None

def fluxerr2magerr(fluxerr, flux):
    # Compute dmag from dflux using derivative of above
    if abs(flux) < 1.0: return 0.0
    else:               return 1.086 * fluxerr / flux

def plotList(alert, pointList, size, symbol, distanceMpc):
    """ Plot one of the three types: 
        diaSource, diaForcedSource, diaNondetectionLimit
    using all 6 colors for different filterNames
    """
    for filterName, color in filterColor.items():
        flux = []
        fluxerr = []
        fluxdays = []
        for s in alert[pointList]:
            if s['filtername'] == filterName:
                flux.append(s['psflux'])
                if 'psfluxerr' in s: 
                    fluxerr.append(s['psfluxerr'])
                else:
                    fluxerr.append(0.0)    # HACK where is psfluxerr ???
                fluxdays.append(s['midpointtai'])
        dflux = pd.DataFrame({'flux':flux, 'fluxerr':fluxerr, 'fluxdays':fluxdays})
        mjd = Time(dflux['fluxdays'], format='mjd')
        dflux['utc'] = mjd.iso
        dflux['utc'] = pd.to_datetime(dflux['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        dflux['name'] = '%s-detection %s' % (filterName, pointList)

        # add traces to row=1, col=1
        fig.add_trace(go.Scatter(
            x=dflux['utc'], 
            y=dflux['flux'],
            error_y = {'type':'data', 'array':dflux['fluxerr']},
            mode='markers', 
            marker=dict(color=color, size=size, symbol=symbol),
            xaxis='x', yaxis='y1',
            customdata=np.stack((dflux['utc'], dflux['flux'], dflux['fluxdays']), axis=-1),
            hovertemplate="<b>" + dflux["name"] + "</b><br>" +
                    "MJD: %{customdata[2]:.2f}<br>" +
                    "UTC: %{customdata[0]}<br>" +
                    "Flux: %{customdata[1]:.0f} μJy<br>" +
                    "<extra></extra>",
        ))
    
        if distanceMpc:
            fig.add_trace(go.Scatter(
                x=dflux['utc'], 
                y=nuLnuLsun*dflux['flux'],
                error_y = {'type':'data', 'array':nuLnuLsun*dflux['fluxerr']},
                mode='markers', marker=dict(color=color, size=size, symbol=symbol),
                xaxis='x', yaxis='y2',
                customdata=np.stack((dflux['utc'], dflux['flux'], dflux['fluxdays']), axis=-1),
                hovertemplate="<b>" + dflux["name"] + "</b><br>" +
                    "MJD: %{customdata[2]:.2f}<br>" +
                    "UTC: %{customdata[0]}<br>" +
                    "Flux: %{customdata[1]:.0f} μJy<br>" +
                    "<extra></extra>",
            ))
    
        mag    = []
        magerr = []
        magdays = []
        for i in range(len(flux)):
            m = flux2mag(flux[i])
            if m:
                magdays.append(fluxdays[i])
                mag.append(m)
                magerr.append(fluxerr2magerr(fluxerr[i], flux[i]))
        dmag  = pd.DataFrame({'mag':mag, 'magerr':magerr, 'magdays':magdays})
        mjd = Time(dmag['magdays'], format='mjd')
        dmag['utc'] = mjd.iso
        dmag['utc'] = pd.to_datetime(dmag['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        dmag['name'] = '%s-detection %s' % (filterName, pointList)

        #Add traces to  row=1, col=2
        fig.add_trace(go.Scatter(
            x=dmag['utc'], 
            y=dmag['mag'],
            error_y = {'type':'data', 'array':dmag['magerr']},
            mode='markers', marker=dict(color=color, size=size, symbol=symbol),
            xaxis='x2', yaxis='y3',
            customdata=np.stack((dmag['utc'], dmag['mag'], dmag['magdays']), axis=-1),
            hovertemplate="<b>" + dmag["name"] + "</b><br>" +
                "MJD: %{customdata[2]:.2f}<br>" +
                "UTC: %{customdata[0]}<br>" +
                "Magnitude: %{customdata[1]:.1f}<br>" +
                "<extra></extra>",
        ))
    
        if distanceMpc:
            fig.add_trace(go.Scatter(
                x=dmag['utc'], 
                y=magAbs + dmag['mag'],
                error_y = {'type':'data', 'array':dmag['magerr']},
                mode='markers', marker=dict(color=color, size=size, symbol=symbol),
                xaxis='x2', yaxis='y4',
                customdata=np.stack((dmag['utc'], dmag['mag'], dmag['magdays']), axis=-1),
                hovertemplate="<b>" + dmag["name"] + "</b><br>" +
                    "MJD: %{customdata[2]:.2f}<br>" +
                    "UTC: %{customdata[0]}<br>" +
                    "Magnitude: %{customdata[1]:.1f}<br>" +
                    "<extra></extra>",
            ))
    
def object_difference_lightcurve(alert):
    """ 
    Plot the entire alert with its 6 colors and 3 types of symbol
    """
    global fig, nuLnuLsun, magAbs

    if 'sherlock' in alert and 'distance' in alert['sherlock']:
        distanceMpc = alert['sherlock']['distance']

    flux = []
    fluxerr = []
    fluxdays = []

    for s in alert['diaSources']:
        flux.append(s['psflux'])
        fluxerr.append(s['psfluxerr'])
        fluxdays.append(s['midpointtai'])

    for s in alert['diaForcedSources']:
        flux.append(s['psflux'])
        if 'psfluxerr' in s:
            fluxerr.append(s['psfluxerr'])
        else:
            fluxerr.append(0.0)         # HACK why no psfluxerr????
        fluxdays.append(s['midpointtai'])

    for s in alert['diaNondetectionLimits']:
        s['psflux'] = s['dianoise']
        s['psfluxErr'] = 0.0
        flux.append(s['psflux'])
        fluxerr.append(s['psfluxerr'])
        fluxdays.append(s['midpointtai'])

    fluxMin =  0
    fluxMax = -100000000
    for i in range(len(flux)):
        if flux[i] and flux[i] + fluxerr[i] > fluxMax: fluxMax = flux[i] + fluxerr[i]
        if flux[i] and flux[i] - fluxerr[i] < fluxMin: fluxMin = flux[i] - fluxerr[i]
    d = fluxMax-fluxMin
    fluxMin -= 0.02*d
    fluxMax += 0.02*d
    
    mag    = []
    magerr = []
    magdays = []
    for i in range(len(flux)):
        m = flux2mag(flux[i])
        if m:
            magdays.append(fluxdays[i])
            mag.append(m)
            magerr.append(fluxerr2magerr(fluxerr[i], flux[i]))
    
    magMin =  100000000
    magMax = -100000000
    for i in range(len(mag)):
        if mag[i] and mag[i] + magerr[i] > magMax: magMax = mag[i] + magerr[i]
        if mag[i] and mag[i] - magerr[i] < magMin: magMin = mag[i] - magerr[i]
    d = magMax-magMin
    magMin -= 0.02*d
    magMax += 0.02*d
    
    if distanceMpc:
        # add to mag to get abs mag
        magAbs    =  - 5*math.log10(distanceMpc) - 25  # add to get abs mag
        nuLnuLsun = distanceMpc*distanceMpc * 0.1563   # multiplier to get abs flux
    
    fig = go.Figure()
    
    #define xaxes, yaxes
    fig.update_layout(
        xaxis =dict(domain=[0.0, 0.8]),
        xaxis2=dict(domain=[0.0, 0.8]),
        
        yaxis1=dict(
            title='difference flux (nJ)',
            anchor='free', side='left',
            range=[fluxMin,fluxMax],
            domain=[0.525, 1.0],
        ),
        yaxis3=dict(
            title='difference magnitude',
            anchor='free', side='left',
            ticks='outside',
            range=[magMax, magMin],
            domain=[0.0, 0.475],
        ),
    )
    
    if distanceMpc:
        fig.update_layout(
            yaxis2=dict(
                title='nuLnu/Lsun',
                anchor='x', side='right',
                range=[nuLnuLsun*fluxMin,nuLnuLsun*fluxMax],
                domain=[0.525, 1.0],
            ),
        
            yaxis4=dict(
                title='absolute magnitude',
                anchor='x2', side='right',
                range=[magMax+magAbs, magMin+magAbs],
                domain=[0.05, 0.475],
            ),
        )

    # Now we can make the three plots, each with 6 colors
    plotList(alert, 'diaSources',            12, 'circle',          distanceMpc)
    plotList(alert, 'diaForcedSources',       8, 'square',          distanceMpc)
    plotList(alert, 'diaNondetectionLimits',  5, 'arrow-down-open', distanceMpc)

    fig.update_layout(
        width =1000,
        height=1000,
        showlegend=False,
        hoverlabel=dict(
            font_color="white",
            bgcolor="#1F2937",
            font_size=14,
        )
    )
    htmlLightcurve = fig.to_html(
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': 
                {'filename': str(alert['diaObjectId']) + '_lasair_lc'},
            'responsive': True
        })
    return htmlLightcurve

if __name__ == '__main__':
    import sys,json
    alert = json.loads(open('4006.json').read())
    if len(sys.argv) > 1:
        alert['sherlock'] = {}
        alert['sherlock']['distance'] = float(sys.argv[1])
    
    htmlLightcurve = object_difference_lightcurve(alert)
    fig.show()

# Compute the nuLnu luminosity of a source given:
# -- flux f measured in nanoJansky
# -- distance D measured in megaParsec
# -- we choose fixed nu from the middle of the optical band, 600 nm
# 
# (1) Definition of jansky is 1.e-23 erg/s/cm2/Hz
# Since f is nano Jamsky, we have flux = 1.e-32 f in erg/s/cm2/Hz
# 
# (2) Definition of parsec     = 3.0857e18     cm
# Since D is Mpc, the distance   = 3.0857e24 D   cm
# 
# (3) Chosen wavelength = lambda = 600 nanometers = 6.0e-5  cm
# nu = central frequency = c/lambda
#     = 2.998e10/(6.0e-5)
#     = 5.000e14 Hz
# 
# (4) nuLnu = (5.000e14) x 4pi x (3.0857e24 D)^2 x (1.e-32 f)
#     = (D^2 f) x 598.3e30 erg/sec
#     = (D^2 f) x 5.983e32 erg/sec
#     = (D^2 f) x 5.983e25 watts
# 
# (5) Luminosity of sun = 3.828e26 W
#     so nuLnu/Lsun = (D^2 f) x 0.1563
