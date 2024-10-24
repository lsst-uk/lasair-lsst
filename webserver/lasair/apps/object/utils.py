import pandas as pd
from astropy.time import Time
import plotly.graph_objects as go
import math, json
import numpy as np

bands  = ['u', 'g', 'r', 'i', 'z', 'y']
bandColors = ["#9900cc", "#3366ff", "#33cc33", "#ffcc00", "#ff0000", "#cc6600"]

def object_difference_lightcurve(
    objectData
):
    """*Generate the Plotly HTML lightcurve for the object*

    **Key Arguments:**

    - ``objectData`` -- a json object containing lightcurve data (and more)

    **Usage:**

    ```python
    from lasair.apps.objects.utils import object_difference_lightcurve
    htmlLightcurve = object_difference_lightcurve(data)
    ```
    """
    # CREATE DATA FRAME FOR LC
    forcedDF, unforcedDF, mergedDF = convert_objectdata_to_dataframes(objectData)

    # FILTER DATA FRAME
    unforcedDF["marker_color"] = "#268bd2"
    unforcedDF["marker_symbol"] = "arrow-bar-down-open"
    unforcedDF["marker_size"] = 8
    unforcedDF["marker_opacity"] = 0.6
    unforcedDF["name"] = "anon"
    symbol_sequence = ["arrow-bar-down-open", "circle"]

    for bandColor,band in zip(bandColors, bands):
        unforcedDF.loc[(unforcedDF['band'] == band), "marker_color"] = bandColor
        unforcedDF.loc[(unforcedDF['band'] == band), "bcolor"] = bandColor

    unforcedDF["marker_symbol"] = "circle"
    unforcedDF["marker_size"]   = 10

    # SORT BY COLUMN NAME
    discovery = unforcedDF.head(1)

    # GENERATE THE DATASETS
    allDataSets = []

    for band in bands:
        BandData = unforcedDF.loc[(unforcedDF['band'] == band)]
        BandData["name"] = band + "-band flux detection"
        allDataSets.append(BandData)

    # START TO PLOT
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()

    for data in allDataSets:
        if len(data.index):
            dataType = "Diff Mag"
            error_y = {'type': 'data', 'array': data["sigmapsf"]}
            fig.add_trace(

                go.Scatter(
                    x=data["mjd"],
                    y=data["magpsf"],
                    customdata=np.stack((data['utc'], data['magpsf'], data['sigmapsf']), axis=-1),
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
                    "Magnitude: %{customdata[1]:.2f} ± %{customdata[2]:.2f}" +
                    "<extra></extra>",
                ),
                secondary_y=False
            )
            fig.add_traces(
                go.Scatter(x=data["utc"],
                           y=data["magpsf"],
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, magMin, magMax = get_default_axis_ranges(forcedDF, unforcedDF)

    if forcedDF is None:
        title = "MJD"
        tickfont_size = 14
        title_font_size = 1
    else:
        title = ""
        tickfont_size = 11
        title_font_size = 16

    fig.update_xaxes(range=[mjdMin, mjdMax], tickformat='d', tickangle=-55, tickfont_size=tickfont_size, showline=True, linewidth=1.5, linecolor='#1F2937',
                     gridcolor='#F0F0F0', gridwidth=1,
                     zeroline=True, zerolinewidth=1.5, zerolinecolor='#1F2937', ticks='inside', title=title, title_font_size=title_font_size)
    fig.update_layout(xaxis2={'range': [utcMin, utcMax],
                              'showgrid': False,
                              'anchor': 'y',
                              'overlaying': 'x',
                              'side': 'top',
                              'tickangle': -55,
                              'tickfont_size': 14,
                              'showline': True,
                              'linewidth': 1.5,
                              'linecolor': '#1F2937'})

    fig.update_yaxes(
        range=[magMax, magMin],
        tickformat='.1f',
        tickfont_size=14,
        ticksuffix=" ",
        showline=True,
        showgrid=True,
        linewidth=1.5,
        linecolor='#1F2937',
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        mirror=True,
        ticks='inside',
        title="Difference Magnitude",
        title_font_size=16,
        secondary_y=False,
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
        )
    )

    fig.add_trace(go.Scatter(
        x=discovery["mjd"],
        y=[magMax - 0.05],
        mode="markers+text",
        marker_symbol="triangle-up",
        marker_opacity=1,
        marker_color="#1F2937",
        marker_size=8,
        showlegend=False,
        text=["Discovery Epoch"],
        textposition="middle right"
    ))

    fig.update_layout(
        title=dict(text="Standard Photometry Magnitudes", font=dict(size=20), y=0.85,
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
        })

    return htmlLightcurve, mergedDF


def object_difference_lightcurve_forcedphot(
    objectData
):
    """*Generate the Plotly HTML lightcurve for the object force photometry*

    **Key Arguments:**

    - ``objectData`` -- a json object containing lightcurve data (and more)

    **Usage:**

    ```python
    from lasair.apps.objects.utils import object_difference_lightcurve_forcedphot
    htmlLightcurve = object_difference_lightcurve_forcedphot(data)
    ```
    """
    forcedDF, unforcedDF, mergedDF = convert_objectdata_to_dataframes(objectData)

    if forcedDF is None:
        return None, None

    # FILTER DATA FRAME
    forcedDF["marker_color"] = "#268bd2"
    forcedDF["bcolor"] = "#268bd2"
    forcedDF["marker_symbol"] = "arrow-bar-down-open"
    forcedDF["marker_size"] = 8
    forcedDF["marker_opacity"] = 0.6
    forcedDF["name"] = "anon"
    symbol_sequence = ["arrow-bar-down-open", "circle"]
    for bandColor,band in zip(bandColors, bands):
        forcedDF.loc[(forcedDF['band'] == band), "marker_color"] = bandColor
        forcedDF.loc[(forcedDF['band'] == band), "bcolor"] = bandColor

    forcedDF["marker_symbol"] = "circle"
    forcedDF["marker_size"] = 10

    discovery = unforcedDF.head(1)

    # GENERATE THE DATASETS
    allDataSets = []
    for band in bands:
        BandDetections = forcedDF.loc[(forcedDF['band'] == band)]
        BandDetections["name"] = band + "-band detection"
        allDataSets.append(BandDetections)

    # START TO PLOT
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()

    for data in allDataSets:
        if len(data.index):
            dataType = "Diff Flux"
            error_y = {'type': 'data', 'array': data["nanojanskyerr"]}
            fig.add_trace(

                go.Scatter(
                    x=data["midpointmjdtai"],
                    y=data["nanojansky"],
                    customdata=np.stack((data['utc'], data['nanojansky'], data['nanojanskyerr']), axis=-1),
                    error_y=error_y,
                    error_y_thickness=0.7,
                    error_y_color=data["bcolor"].values[0],
                    mode='markers',
                    showlegend=True,
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
                    "Flux: %{customdata[1]:.2f} ± %{customdata[2]:.2f} μJy" +
                    "<extra></extra>",
                ),
                secondary_y=False
            )

            fig.add_traces(
                go.Scatter(x=data["utc"],
                           y=data["nanojansky"],
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, magMin, magMax = get_default_axis_ranges(forcedDF, unforcedDF)

    fig.update_xaxes(range=[mjdMin, mjdMax], tickformat='d', tickangle=-55, tickfont_size=14, showline=True, linewidth=1.5, linecolor='#1F2937',
                     gridcolor='#F0F0F0', gridwidth=1,
                     zeroline=True, zerolinewidth=1.5, zerolinecolor='#1F2937', ticks='inside', title="MJD", title_font_size=16)
    fig.update_layout(xaxis2={'range': [utcMin, utcMax],
                              'showgrid': False,
                              'anchor': 'y',
                              'overlaying': 'x',
                              'side': 'top',
                              'tickangle': -55,
                              'tickfont_size': 11,
                              'showline': True,
                              'linewidth': 1.5,
                              'linecolor': '#1F2937'})

    fig.update_yaxes(
        range=[fluxMin, fluxMax],
        tickformat='.1f',
        tickfont_size=14,
        ticksuffix=" ",
        showline=True,
        linewidth=1.5,
        linecolor='#1F2937',
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=3.0,
        zerolinecolor='rgba(60, 60, 60, 0.8)',
        mirror=True,
        ticks='inside',
        title="Difference Flux (nanoJy)",
        title_font_size=16,
        secondary_y=False
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
        )
    )

    fig.add_trace(go.Scatter(
        x=discovery["mjd"],
        y=[10],
        mode="markers+text",
        marker_symbol="triangle-up",
        marker_opacity=1,
        marker_color="#1F2937",
        marker_size=8,
        showlegend=False,
        text=["Discovery Epoch"],
        textposition="middle right"
    ))

    fig.update_layout(
        title=dict(text="Forced Photometry Flux", font=dict(size=20), y=0.87,
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
        })

    return htmlLightcurve, mergedDF


def get_default_axis_ranges(
        forcedDF,
        unforcedDF):
    """*get the default x and y-axis ranges for the lightcurve plots*

    **Key Arguments:**

    - `forcedDF` -- forced photometry dataframe
    - `unforcedDF` -- unforced photometry dataframe    
    """

    mjdMin = unforcedDF["midpointmjdtai"].min()
    mjdMax = unforcedDF["midpointmjdtai"].max()

    if forcedDF is not None:
# question: Whats going on here
#        mjdMin2 = forcedDF.loc[((forcedDF['forcediffimflux'] > 50) & (forcedDF['forcediffimfluxunc'] < 50)), "mjd"].min()
#        mjdMax2 = forcedDF.loc[((forcedDF['forcediffimflux'] > 50) & (forcedDF['forcediffimfluxunc'] < 50)), "mjd"].max()
        mjdMin2 = forcedDF["midpointmjdtai"].min()
        mjdMax2 = forcedDF["midpointmjdtai"].max()

        if mjdMin2 < mjdMin:
            mjdMin = mjdMin2
        if mjdMax2 > mjdMax:
            mjdMax = mjdMax2

    # SORT BY COLUMN NAME
    discovery = unforcedDF.head(1)
    if mjdMin > discovery["midpointmjdtai"].min():
        mjdMin = discovery["midpointmjdtai"].min()

    mjdRange = mjdMax - mjdMin
    if mjdRange < 5:
        mjdRange = 5
    mjdMin -= 4 + mjdRange * 0.05
    mjdMax += 2 + mjdRange * 0.05

    utcMin = Time(mjdMin, format='mjd').iso
    utcMax = Time(mjdMax, format='mjd').iso

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    if forcedDF is not None:
        fluxMax = forcedDF.loc[((forcedDF['midpointmjdtai'] > mjdMin) & \
                (forcedDF['midpointmjdtai'] < mjdMax)), "nanojansky"] + forcedDF.loc[((forcedDF['midpointmjdtai'] > mjdMin) & \
                (forcedDF['midpointmjdtai'] < mjdMax)), "nanojanskyerr"]
        fluxMax = fluxMax.max()
        fluxMin = forcedDF.loc[((forcedDF['midpointmjdtai'] > mjdMin) & \
                (forcedDF['midpointmjdtai'] < mjdMax)), "nanojansky"] - forcedDF.loc[((forcedDF['midpointmjdtai'] > mjdMin) & \
                (forcedDF['midpointmjdtai'] < mjdMax)), "nanojanskyerr"]
        fluxMin = fluxMin.min()

        yrange = fluxMax - fluxMin
        if yrange < 50:
            yrange = 50
        fluxMax += (yrange * 0.1)
        fluxMin -= (yrange * 0.1)

        if fluxMin > 0:
            fluxMin = 0
    else:
        fluxMin, fluxMax = None, None

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    unforcedDF["tmpSigmapsf"] = 0

    unforcedDF.loc[(unforcedDF['sigmapsf'] > 0), "tmpSigmapsf"] = unforcedDF.loc[(unforcedDF['sigmapsf'] > 0), "sigmapsf"]
    unforcedDF["tmpSigmapsf"]
    unforcedDF.loc[((unforcedDF['mjd'] > mjdMin) & (unforcedDF['mjd'] < mjdMax)), "sigmapsf"] = 0
    magMax = unforcedDF.loc[((unforcedDF['mjd'] > mjdMin) & (unforcedDF['mjd'] < mjdMax)), "magpsf"] + unforcedDF.loc[((unforcedDF['mjd'] > mjdMin) & (unforcedDF['mjd'] < mjdMax)), "tmpSigmapsf"]
    magMax = magMax.max()
    magMin = unforcedDF.loc[((unforcedDF['mjd'] > mjdMin) & (unforcedDF['mjd'] < mjdMax)), "magpsf"] - unforcedDF.loc[((unforcedDF['mjd'] > mjdMin) & (unforcedDF['mjd'] < mjdMax)), "tmpSigmapsf"]
    magMin = magMin.min()

    yrange = magMax - magMin
    if yrange < 3:
        yrange = 3
    magMax += (yrange * 0.1)
    magMin -= (yrange * 0.1)

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
        mjds = Time(forcedDF['midpointmjdtai'], format='mjd')
        forcedDF['utc'] = mjds.iso
        forcedDF['utc'] = pd.to_datetime(forcedDF['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        # SORT BY COLUMN NAME
        forcedDF.sort_values(['midpointmjdtai'],
                             ascending=[True], inplace=True)

# Standard naming
        forcedDF["band"] = forcedDF['band']
        forcedDF["nanojansky"] = forcedDF['psfflux']
        forcedDF["nanojanskyerr"] = forcedDF['psffluxerr']

# Convert from flux nJ to mag
        forcedDF["magpsf"]   = 31.4 - 2.5*np.log10(forcedDF["nanojansky"])
        forcedDF["sigmapsf"] = 1.086 * forcedDF["nanojanskyerr"] / forcedDF["nanojansky"]

    if forcedDF is not None and len(forcedDF.index) == 0:
        forcedDF = None

    # NORMAL UNFORCED PHOTO
    if len(objectData["diaSources"]):
        unforcedDF = pd.DataFrame(objectData["diaSources"])
        mjds2 = Time(unforcedDF['midpointmjdtai'], format='mjd')
        unforcedDF['utc'] = mjds2.iso
        unforcedDF['utc'] = pd.to_datetime(unforcedDF['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        unforcedDF.sort_values(['midpointmjdtai'],
                               ascending=[True], inplace=True)
# Standard naming
        unforcedDF["nanojansky"] = unforcedDF['psfflux']
        unforcedDF["nanojanskyerr"] = unforcedDF['psffluxerr']
# Convert from flux nJ to mag
        unforcedDF["magpsf"]   = 31.4 - 2.5*np.log10(unforcedDF["nanojansky"])
        unforcedDF["sigmapsf"] = 1.086 * unforcedDF["nanojanskyerr"] / unforcedDF["nanojansky"]

    # MATCH THE FORCED AND UNFORCED TABLES
    if forcedDF is not None:
        mergedDF = pd.merge(unforcedDF, \
            forcedDF[['nanojansky', 'nanojanskyerr', 'midpointmjdtai', 'band']], \
            how='left', on=['midpointmjdtai', 'band'])
    else:
        mergedDF = unforcedDF
        mergedDF['nanojansky'] = np.nan
        mergedDF['nanojanskyerr'] = np.nan
    mergedDF = mergedDF.replace({np.nan: None})
    mergedDF.sort_values(['mjd'], ascending=[False], inplace=True)

    return forcedDF, unforcedDF, mergedDF

# use the tab-trigger below for new function
# xt-def-function
