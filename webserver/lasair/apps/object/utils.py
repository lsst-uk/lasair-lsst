import pandas as pd
from astropy.time import Time
import plotly.graph_objects as go
import math, json
import numpy as np

# THESE ARE THE RUBIN STYLE GUIDE COLOURS AND SYMBOLS
bands  = ['u', 'g', 'r', 'i', 'z', 'y']
bandColors = ['#1600ea', '#31de1f', '#b52626', '#370201', '#ba52ff', '#61a2b3']
bandSymbols = ['circle', 'triangle-up', 'triangle-down', 'square', 'star', 'hexagon']
bandColorsDark = ['#3eb7ff','#30c39f','#ff7e00', '#2af5ff','#a7f9c1','#fdc900']

# BOTH SIDEBARS SET TO BLACK
magcolor  = '#002b36'
fluxcolor = '#002b36'

def flux2mag(flux):   # nanoJansky to Magnitude
    if flux > 0: 
        mag = 31.4 - 2.5 * math.log10(flux)
        return mag
    else:        
        return None
    
    
def mag2flux(mag):    # Magnitude to nanoJansky
    return math.pow(10.0, (31.4 - mag)/2.5)

def object_difference_lightcurve(
    objectData,
    forced=False
):
    """*Generate the Plotly HTML lightcurve for the object*

    **Key Arguments:**

    - ``objectData`` -- a json object containing lightcurve data (and more)
    - ``forced`` -- a boolean indicating whether to use forced photometry or not

    **Usage:**

    ```python
    from lasair.apps.objects.utils import object_difference_lightcurve
    htmlLightcurve = object_difference_lightcurve(data)
    ```
    """

    from plotly.subplots import make_subplots

    # CREATE DATA FRAME FOR LC
    forcedDF, unforcedDF, mergedDF = convert_objectdata_to_dataframes(objectData)
    

    if forced:
        lcDF = unforcedDF 
    else:
        lcDF = unforcedDF
        forcedDF = unforcedDF

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, magMin, magMax = get_default_axis_ranges(lcDF)

    # DEFAULT DATA FRAME
    lcDF["marker_color"] = "#268bd2"
    lcDF["marker_symbol"] = "arrow-bar-down-open"
    lcDF["marker_size"]   = 10
    lcDF["marker_opacity"] = 0.6
    lcDF["name"] = "anon"

    for bandColor,band,symbol in zip(bandColors, bands, bandSymbols):
        lcDF.loc[(lcDF['band'] == band), "marker_color"] = bandColor
        lcDF.loc[(lcDF['band'] == band), "bcolor"] = bandColor
        lcDF.loc[(lcDF['band'] == band), "marker_symbol"] = symbol

    # SORT BY COLUMN NAME ... DISCOVERY IS ALWAYS FROM UNFORCED DATA
    discovery = unforcedDF.head(1)

    # GENERATE THE DATASETS
    allDataSets = []

    for band in bands:
        BandData = lcDF.loc[(lcDF['band'] == band)]
        BandData["name"] = band + "-band"
        allDataSets.append(BandData)

    # START PLOTTING
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for data in allDataSets:
        if len(data.index):
            error_y = {'type': 'data', 'array': data["nanojanskyerr"], 'visible': True}
            fig.add_trace(
                go.Scatter(
                    x=data["mjd"],
                    y=data["nanojansky"],
                    customdata=np.stack((data['utc'], data['nanojansky'], data['magpsf']), axis=-1),
                    error_y=error_y,
                    error_y_thickness=0.7,
                    error_y_color=data["bcolor"].values[0],
                    mode='markers',
                    marker_size=data["marker_size"].values[0],
                    marker_color=data["marker_color"].values[0],
                    marker_symbol=data["marker_symbol"].values[0],
                    marker_line_color=data["bcolor"].values[0],
                    marker_line_width=1.5,
                    marker_opacity=data["marker_opacity"].values[0],
                    name=data["name"].values[0],
                    hovertemplate="<b>" + data["name"] + "</b><br>" +
                        "MJD: %{x:.2f}<br>" +
                        "UTC: %{customdata[0]}<br>" +
                        "Flux: %{customdata[1]:.2f} nJy<br>" +
                        "Magnitude: %{customdata[2]:.2f}" +
                        "<extra></extra>",
                ),
                secondary_y=False
            )
            ## REPLOT THE SAME DATA ON THE RHS AXIS (BUT HIDDEN)
            fig.add_trace(
                go.Scatter(
                    x=data["mjd"],
                    y=data["nanojansky"],
                    customdata=np.stack((data['utc'], data['nanojansky'], data['magpsf']), axis=-1),
                    mode='markers',
                    marker_size=data["marker_size"].values[0],
                    marker_color="#268bd2",
                    marker_symbol=data["marker_symbol"].values[0],
                    marker_line_color=data["bcolor"].values[0],
                    marker_line_width=1.5,
                    marker_opacity=data["marker_opacity"].values[0],
                    name=data["name"].values[0],
                    hoverinfo='skip',
                    opacity=0,
                    showlegend=False
                ),
                secondary_y=True
            )
            # REPLOT FOR THE TOP X-AXIS
            fig.add_traces(
                go.Scatter(x=data["utc"],
                           y=data["nanojansky"],    
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    if forced or (forcedDF is None and not forced):
        btitle = "MJD"
        btickfont_size = 14
        btitle_font_size = 16
    else:
        btitle = ""
        btickfont_size = 11
        btitle_font_size = 16
        

    if forced:
        ttitle = ""
        ttickfont_size = 11
        ttitle_font_size = 16
    else:
        ttitle = "UTC Time"
        ttickfont_size = 14
        ttitle_font_size = 16

    fig.update_layout(
        xaxis=dict(
            side="bottom",
            range=[mjdMin, mjdMax],
            tickformat='d',
            tickangle=-55,
            tickfont_size=btickfont_size,
            showline=True,
            linewidth=1.5,
            linecolor='#1F2937',
            gridcolor='#F0F0F0',
            gridwidth=1,
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor='#1F2937',
            ticks='inside',
            title=dict(text=btitle), 
            title_font_size=btitle_font_size
        ),
        xaxis2=dict(
            title=dict(text=ttitle),
            title_font_size=ttitle_font_size,
            tickfont_size=ttickfont_size,
            side="top",
            range=[utcMin, utcMax],
            overlaying="x",
            tickmode="sync",
            tickangle=-55,
            showline=True,
            linewidth=1.5,
            linecolor='#1F2937'
        )
    )

    # Define the tick values for the secondary y-axis
    rangeFlux = fluxMax - fluxMin
    tickvals = np.linspace(fluxMin-rangeFlux*5, fluxMax+rangeFlux*5,  70)

    # Convert tick values to the desired format
    ticktext = [f'{flux2mag(val):.2f}' if val > 0 else '' for val in tickvals]

    fig.update_yaxes(
        range=[fluxMin, fluxMax],
        tickformat='.0f',
        tickfont_size=14,
        ticksuffix=" ",
        tickfont_color=fluxcolor,
        showline=True,
        showgrid=True,
        linewidth=1.5,
        linecolor='#1F2937',
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        ticks='inside',
        title="Difference Flux (nanoJy)",
        title_font_size=14,
        title_font_color=fluxcolor,
        secondary_y=False,

    )

    fig.update_yaxes(   # RDW:log right axis
        range=[fluxMin, fluxMax],  # Inverted range
        secondary_y=True,   # right side
        showgrid=True,
        tickformat='.2f',
        tickfont_size=14,
        tickfont_color=magcolor,
        tickcolor=magcolor,
        ticksuffix=" ",
        showline=True,
        linewidth=1.5,
        linecolor='#1F2937',
        ticks='inside',
        title_text="Difference Magnitude (AB)",
        title_font_size=16,
        title_font_color=magcolor,
        tickvals=tickvals,  # Original tick values
        ticktext=ticktext,    # Converted tick labels
        overlaying="y",
        matches="y"  # Keep the two y-axes in sync
    )

    # UPDATE PLOT LAYOUT
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=550,
        margin_t=0,
        margin_b=0,
        margin_r=1,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=0,
            bgcolor="#E6E5E5",
            borderwidth=4,
            bordercolor="#E6E5E5",
        ),
        hoverlabel=dict(
            font_color="white",
            bgcolor="#1F2937",
            font_size=14,
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=True,
                font=dict(color="#D1D5DB"),
                bgcolor="#6B7280",
                borderwidth=1,
                bordercolor="#D1D5DB",
                x=-0.03,  # Horizontal position (0 to 1)
                y=1.02,  # Vertical position (above the plot)
                xanchor="center",  # Anchor the button group at the center
                yanchor="bottom",     # Anchor the button group at the top
                buttons=[
                    dict(
                        label="Log",
                        method="relayout",
                        args=[{"yaxis.type": "linear", "yaxis2.type": "linear", "updatemenus[0].font.color": "#D1D5DB", "updatemenus[0].bgcolor": "#6B7280"}],
                        args2=[{"yaxis.type": "log","yaxis2.type": "log","updatemenus[0].font.color": "#E11D48", "updatemenus[0].bgcolor": "#D1D5DB"}],
                    ),
                ],
            )
        ]
    )

    fig.add_trace(go.Scatter(
        x=discovery["mjd"],
        y=[fluxMin*1.08],
        mode="markers+text",
        marker_symbol="triangle-up",
        marker_opacity=1,
        marker_color="#1F2937",
        marker_size=8,
        showlegend=False,
        text=["Discovery Epoch"],
        textposition="middle right"
    ))

    if forced:
        title_text = "Forced Photometry Flux"
        y=0.82
    else:
        title_text = "Standard Photometry Flux"
        y=0.80

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20), y=y,
                   x=0.5,
                   xanchor='center',
                   yanchor='top',
                   font_color="#657b83",)
    )

    htmlLightcurve = fig.to_html(
        config={
            'displayModeBar': False,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'filename': objectData["diaObjectId"] + "_lasair_lc"},
            'responsive': True
        },post_script="""
            document.addEventListener("DOMContentLoaded", function() {
                let scrollers = document.querySelectorAll('.x2y');
                scrollers.forEach(function(scroller) {
                    scroller.remove();
                });
            });
        """)

    return htmlLightcurve, mergedDF

def get_default_axis_ranges(
        lcDF):
    """*get the default x and y-axis ranges for the lightcurve plots*

    **Key Arguments:**

    - `lcDF` -- licghtcurve dataframe
    """

    mjdMin = lcDF["midpointMjdTai"].min()
    mjdMax = lcDF["midpointMjdTai"].max()

    # SORT BY COLUMN NAME
    discovery = lcDF.head(1)
    if mjdMin > discovery["midpointMjdTai"].min():
        mjdMin = discovery["midpointMjdTai"].min()

    mjdRange = mjdMax - mjdMin
    if mjdRange < 3:
        mjdRange = 3
    mjdMin -= 4 + mjdRange * 0.05
    mjdMax += 2 + mjdRange * 0.05

    utcMin = Time(mjdMin, format='mjd').iso
    utcMax = Time(mjdMax, format='mjd').iso

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    fluxMax = lcDF.loc[((lcDF['midpointMjdTai'] > mjdMin) & \
            (lcDF['midpointMjdTai'] < mjdMax)), "nanojansky"] + lcDF.loc[((lcDF['midpointMjdTai'] > mjdMin) & \
            (lcDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
    fluxMax = fluxMax.max()
    fluxMin = lcDF.loc[((lcDF['midpointMjdTai'] > mjdMin) & \
            (lcDF['midpointMjdTai'] < mjdMax)), "nanojansky"] - lcDF.loc[((lcDF['midpointMjdTai'] > mjdMin) & \
            (lcDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
    fluxMin = fluxMin.min()
    if fluxMin < 0 and fluxMax < 0:
        fluxMax = 0

    yrange = fluxMax - fluxMin
    fluxMax += (yrange * 0.1)
    fluxMin -= (yrange * 0.1)

    magMin = flux2mag(fluxMin)
    magMax = flux2mag(fluxMax)

    return mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, magMin, magMax

def convert_objectdata_to_dataframes(
        objectData):
    """*return a forced photometry and unforce photometry dataframe from the objectdata*

    **Key Arguments:**

    - `objectData` -- the object data (forced and unforced)      
    """
    forcedDF, unforcedDF = None, None

    # CREATE DATA FRAME FOR LC
    if len(objectData["diaForcedSources"]):
        forcedDF = pd.DataFrame(objectData["diaForcedSources"])
        mjds = Time(forcedDF['midpointMjdTai'], format='mjd')
        forcedDF['utc'] = mjds.iso
        forcedDF['utc'] = pd.to_datetime(forcedDF['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        # SORT BY COLUMN NAME
        forcedDF.sort_values(['midpointMjdTai'],
                             ascending=[True], inplace=True)

        # Standard naming
        forcedDF["band"] = forcedDF['band']
        forcedDF["nanojansky"] = forcedDF['psfFlux']
        forcedDF["nanojanskyerr"] = forcedDF['psfFluxErr']

        # Convert from flux nJ to mag
        flux = forcedDF["nanojansky"]
        forcedDF["magpsf"]   = np.where(flux>0, 31.4 - 2.5 * np.log10(flux), 99.0)
        forcedDF["sigmapsf"] = 1.086 * forcedDF["nanojanskyerr"] / forcedDF["nanojansky"]
        

    if forcedDF is not None and len(forcedDF.index) == 0:
        forcedDF = None

    # NORMAL UNFORCED PHOTO
    if len(objectData["diaSources"]):
        unforcedDF = pd.DataFrame(objectData["diaSources"])
        mjds2 = Time(unforcedDF['midpointMjdTai'], format='mjd')
        unforcedDF['utc'] = mjds2.iso
        unforcedDF['utc'] = pd.to_datetime(unforcedDF['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        unforcedDF.sort_values(['midpointMjdTai'],
                               ascending=[True], inplace=True)
        # Standard naming
        unforcedDF["nanojansky"] = unforcedDF['psfFlux']
        unforcedDF["nanojanskyerr"] = unforcedDF['psfFluxErr']
        # Convert from flux nJ to mag
        flux = unforcedDF["nanojansky"]
        unforcedDF["magpsf"]   = np.where(flux>0, 31.4 - 2.5 * np.log10(flux), 99.0)
        unforcedDF["sigmapsf"] = 1.086 * unforcedDF["nanojanskyerr"] / unforcedDF["nanojansky"]

    # MATCH THE FORCED AND UNFORCED TABLES
    if forcedDF is not None:
        mergedDF = pd.merge(unforcedDF, \
            forcedDF[['nanojansky', 'nanojanskyerr', 'midpointMjdTai', 'band']], \
            how='left', on=['midpointMjdTai', 'band'])
    else:
        mergedDF = unforcedDF
    mergedDF = mergedDF.replace({np.nan: None})
    mergedDF.sort_values(['mjd'], ascending=[False], inplace=True)

    return forcedDF, unforcedDF, mergedDF

# use the tab-trigger below for new function
# xt-def-function
