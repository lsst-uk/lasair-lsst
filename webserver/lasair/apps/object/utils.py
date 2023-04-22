import pandas as pd
import plotly.graph_objects as go
import math
import numpy as np

mcolor = {
        'u': '#ff0000',
        'g': '#f00f00',
        'r': '#0f0f00',
        'i': '#00ff00',
        'z': '#00f0f0',
        'y': '#0000ff',
}

bcolor = {
        'u': '#aa0000',
        'g': '#a00a00',
        'r': '#0a0a00',
        'i': '#00aa00',
        'z': '#00a0a0',
        'y': '#0000aa',
}

def object_difference_lightcurve( data):
    """*Generate the Plotly HTML lightcurve for the object*

    **Key Arguments:**

    - ``data`` -- a json object containing lightcurve data (and more)

    **Usage:**

    ```python
    from lasair.apps.objects.utils import object_difference_lightcurve
    htmlLightcurve = object_difference_lightcurve(data)
    ```
    """
    from astropy.time import Time
    allDataSets = []

    # CREATE DATA FRAME FOR diaSources ###########################
    df = pd.DataFrame(data["diaSources"])
    df['mjd'] = df['midpointtai']
    mjds = Time(df['mjd'], format='mjd')
    df['utc'] = mjds.iso
    df['utc'] = pd.to_datetime(df['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df["marker_symbol"] = "circle"
    df["marker_size"] = 12
    df["marker_opacity"] = 0.6
    df["name"] = "anon"
    symbol_sequence = ["arrow-bar-down-open", "circle"]

    df["marker_color"] = df["filtername"]
    df["marker_color"].replace(mcolor, inplace=True)

    df["bcolor"] = df["filtername"]
    df["bcolor"].replace(bcolor, inplace=True)

    df["flux"] = df["psflux"]
    df["fluxerr"] = df["psfluxerr"]
    try:
        df["magpsf"] = 23.9 - math.log10(df["flux"])*2.5
        df["sigmagpsf"] = 1.0857 * df["fluxerr"] / df["flux"]
    except:
        pass
    
    df.sort_values(['mjd'], ascending=[True], inplace=True)
    discovery = df.head(1) 

    for filt in mcolor.keys():
        bandDetections = df.loc[(df['filtername'] == filt)]
        bandDetections["name"] = '%s-band detection'%filt
        allDataSets.append(bandDetections)

    # CREATE DATA FRAME FOR diaForcedSources ###########################
    if len(data['diaForcedSources']) > 0:
        df = pd.DataFrame(data["diaForcedSources"])
        df['mjd'] = df['midpointtai']
        mjds = Time(df['mjd'], format='mjd')
        df['utc'] = mjds.iso
        df['utc'] = pd.to_datetime(df['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df["marker_symbol"] = "arrow-bar-down-open"
        df["marker_size"] = 8
        df["marker_opacity"] = 0.6
        df["name"] = "anon"
        symbol_sequence = ["arrow-bar-down-open", "circle"]

        df["marker_color"] = df["filtername"]
        df["marker_color"].replace(mcolor, inplace=True)
    
        df["bcolor"] = df["filtername"]
        df["bcolor"].replace(bcolor, inplace=True)

        df["flux"] = df["psflux"]
        df["fluxerr"] = 0.0
        try:
            df["magpsf"] = 23.9 - math.log10(df["flux"])*2.5
        except:
            pass

        for filt in mcolor.keys():
            bandDetections = df.loc[(df['filtername'] == filt)]
            bandDetections["name"] = '%s-band forced detection'%filt
            allDataSets.append(bandDetections)

    # CREATE DATA FRAME FOR diaNondetectionLimits ###########################
    if len(data['diaNondetectionLimits']) > 0:
        df = pd.DataFrame(data["diaNondetectionLimits"])
        df['mjd'] = df['midpointtai']
        mjds = Time(df['mjd'], format='mjd')
        df['utc'] = mjds.iso
        df['utc'] = pd.to_datetime(df['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df["marker_symbol"] = "arrow-bar-down-open"
        df["marker_size"] = 5
        df["marker_opacity"] = 0.6
        df["name"] = "anon"
        symbol_sequence = ["arrow-bar-down-open", "circle"]

        df["marker_color"] = df["filtername"]
        df["marker_color"].replace(mcolor, inplace=True)

        df["bcolor"] = df["filtername"]
        df["bcolor"].replace(bcolor, inplace=True)
    
        df["flux"] = df["diaNoise"]
        df["fluxerr"] = 0.0
        try:
            df["magpsf"] = 23.9 - math.log10(df["flux"])*2.5
        except:
            pass

        for filt in mcolor.keys():
            bandDetections = df.loc[(df['filtername'] == filt)]
            bandDetections["name"] = '%s-band nondetection limit'%filt
            allDataSets.append(bandDetections)

    # START TO PLOT
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()

    for curve in allDataSets:
        if len(curve.index):
            dataType = "Diff Mag"
            error_y = {'type': 'data', 'array': curve["fluxerr"]}
            fig.add_trace(

                go.Scatter(
                    x=curve["mjd"],
                    y=curve["flux"],
                    customdata=np.stack((curve['utc'], curve['flux'], curve['fluxerr']), axis=-1),
                    error_y=error_y,
                    error_y_thickness=0.7,
                    error_y_color=curve["bcolor"].values[0],
                    mode='markers',
                    marker_size=curve["marker_size"].values[0],
                    marker_color=curve["marker_color"].values[0],
                    marker_symbol=curve["marker_symbol"].values[0],
                    marker_line_color=curve["bcolor"].values[0],
                    marker_line_width=1.5,
                    marker_opacity=curve["marker_opacity"].values[0],
                    name=curve["name"].values[0],
                    hovertemplate="<b>" + curve["name"] + "</b><br>" +
                    "MJD: %{x:.2f}<br>" +
                    "UTC: %{customdata[0]}<br>" +
                    "Flux: %{y} μJy<br>" +
                    "Magnitude: %{customdata[1]:.2f} ± %{customdata[2]:.2f}" +
                    "<extra></extra>",
                ),
                secondary_y=False
            )
            fig.add_trace(

                go.Scatter(
                    x=curve["mjd"],
                    y=curve["flux"],
                    showlegend=False,
                    opacity=0,
                    hoverinfo='skip',
                ),
                secondary_y=True
            )
            fig.add_traces(
                go.Scatter(x=curve["utc"],
                           y=curve["flux"],
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin = df["mjd"].min()
    mjdMax = df["mjd"].max()
    mjdRange = mjdMax - mjdMin
    if mjdRange < 5:
        mjdRange = 5
    mjdMin -= 2 + mjdRange * 0.05
    mjdMax += 2 + mjdRange * 0.05

    utcMin = Time(mjdMin, format='mjd').iso
    utcMax = Time(mjdMax, format='mjd').iso

    fig.update_xaxes(range=[mjdMin, mjdMax], tickformat='d', tickangle=-55, tickfont_size=14, showline=True, linewidth=1.5, linecolor='#1F2937',
                     gridcolor='#F0F0F0', gridwidth=1,
                     zeroline=True, zerolinewidth=1.5, zerolinecolor='#1F2937', ticks='inside', title="MJD", title_font_size=16)
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

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    ymax = df["flux"].max()
    ymin = 1e-10
    yrange = ymax - ymin
    if yrange < 50:
        yrange = 50
    ymax += (yrange * 0.1)
    yMagMin = -2.5 * math.log10(ymax) + 23.9
    yMagMax = -2.5 * math.log10(ymin) + 23.9

    # yFluxMax = 10**((23.9 - ymin) / 2.5)
    # yFluxMin = 10**((23.9 - ymax) / 2.5)

    fig.update_yaxes(
        range=[ymin, ymax],
        tickformat='.1f',
        tickfont_size=14,
        ticksuffix=" ",
        showline=True,
        linewidth=1.5,
        linecolor='#1F2937',
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        mirror=True,
        ticks='inside',
        title="Difference Flux (μJy)",
        title_font_size=16,
        secondary_y=False
    )

    magLabels = [21.0, 20.0, 19.5, 19.0, 18.5,
                 18.0, 17.5, 17.0, 16.5, 16.0, 15.5, 15.0]
    if yMagMin < 14:
        magLabels = [20.0, 16.0, 15.0, 14.0,
                     13.0, 12.5, 12.0, 11.5, 11.0]
    elif yMagMin < 17:
        magLabels = [20., 19.,
                     18.0, 17.0, 16.5, 16.0, 15.5, 15.0]
    elif yMagMin < 18:
        magLabels = [20., 19.5, 19.0, 18.5,
                     18.0, 17.5, 17.0, 16.5, 16.0, 15.5, 15.0]
    magFluxes = [10**((23.9 - m) / 2.5) for m in magLabels]
    magLabels = [f"{m:0.1f}" for m in magLabels]

    fig.update_yaxes(
        dict(
            tickmode='array',
            tickvals=magFluxes,
            ticktext=magLabels
        ),
        range=[ymin, ymax],
        tickformat='.1f',
        tickfont_size=14,
        ticksuffix=" ",
        showline=True,
        showgrid=False,
        linewidth=1.5,
        linecolor='#1F2937',
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        ticks='inside',
        title="Difference Magnitude",
        title_font_size=16,
        secondary_y=True,

    )

    # UPDATE PLOT LAYOUT
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=650,
        margin_t=100,
        margin_r=1,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0
        ),
        hoverlabel=dict(
            font_color="white",
            bgcolor="#1F2937",
            font_size=14,
        )
    )

    fig.add_trace(go.Scatter(
        x=discovery["mjd"],
        y=[5],
        mode="markers+text",
        marker_symbol="triangle-up",
        marker_opacity=1,
        marker_color="#1F2937",
        marker_size=8,
        showlegend=False,
        text=["Discovery Epoch"],
        textposition="middle right"
    ))

    htmlLightcurve = fig.to_html(
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'filename': data["diaObjectId"] + "_lasair_lc"},
            'responsive': True
        })

    return htmlLightcurve

# use the tab-trigger below for new function
# xt-def-function
