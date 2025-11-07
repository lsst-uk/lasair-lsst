import pandas as pd
from astropy.time import Time
import plotly.graph_objects as go
import math, json
import numpy as np

# THESE ARE THE RUBIN STYLE GUIDE COLOURS AND SYMBOLS
bands  = ['u', 'g', 'r', 'i', 'z', 'y']
bandColors = ['#1600ea', '#31de1f', '#b52626', '#370201', '#ba52ff', '#61a2b3']
bandsymbols = ['o', '^', 'v', 's', '*', 'p']
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
    # CREATE DATA FRAME FOR LC
    forcedDF, unforcedDF, mergedDF = convert_objectdata_to_dataframes(objectData)

    if forced:
        lcDF = unforcedDF 
    else:
        lcDF = unforcedDF

    # FILTER DATA FRAME
    lcDF["marker_color"] = "#268bd2"
    lcDF["marker_symbol"] = "arrow-bar-down-open"
    lcDF["marker_size"] = 8
    lcDF["marker_opacity"] = 0.6
    lcDF["name"] = "anon"
    symbol_sequence = ["arrow-bar-down-open", "circle"]

    for bandColor,band in zip(bandColors, bands):
        lcDF.loc[(lcDF['band'] == band), "marker_color"] = bandColor
        lcDF.loc[(lcDF['band'] == band), "bcolor"] = bandColor

    lcDF["marker_symbol"] = "circle"
    lcDF["marker_size"]   = 10

    # SORT BY COLUMN NAME
    discovery = lcDF.head(1)

    # GENERATE THE DATASETS
    allDataSets = []

    for band in bands:
        BandData = lcDF.loc[(lcDF['band'] == band)]
        BandData["name"] = band + "-band flux detection"
        allDataSets.append(BandData)

    # START TO PLOT LOG flux
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()

    for data in allDataSets:
        if len(data.index):
            dataType = "Diff Mag"
            error_y = {'type': 'data', 'array': data["nanojanskyerr"]}

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
            fig.add_trace(

                go.Scatter(
                    x=data["mjd"],
                    y=data["magpsf"],
                    customdata=np.stack((data['utc'], data['nanojansky'], data['magpsf']), axis=-1),
                    mode='markers',
                    marker_size=data["marker_size"].values[0],
                    marker_color="#268bd2",
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
                secondary_y=True
            )
            fig.add_traces(
                go.Scatter(x=data["utc"],
                           y=data["nanojansky"],
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, uffluxMin, uffluxMax = get_default_axis_ranges(forcedDF, unforcedDF)

    if forcedDF is None:
        title = "MJD"
        tickfont_size = 14
        title_font_size = 1
    else:
        title = ""
        tickfont_size = 11
        title_font_size = 16

    fig.update_layout(
        legend=dict(orientation="h"),
        xaxis=dict(
            side="bottom",
            range=[mjdMin, mjdMax],
            tickformat='d',
            tickangle=-55,
            tickfont_size=tickfont_size,
            showline=True,
            linewidth=1.5,
            linecolor='#1F2937',
            gridcolor='#F0F0F0',
            gridwidth=1,
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor='#1F2937',
            ticks='inside',
            title=title, 
            title_font_size=title_font_size
        ),
        xaxis2=dict(
            title=dict(text=""),
            side="top",
            range=[utcMin, utcMax],
            overlaying="x",
            tickmode="sync",
            tickangle=-55,
            tickfont_size=14,
            showline=True,
            linewidth=1.5,
            linecolor='#1F2937'
        ),
    )

    fig.update_yaxes(
        range=[uffluxMin, uffluxMax],
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
        mirror=True,
        ticks='inside',
        title="Difference Flux (nanoJy)",
        title_font_size=14,
        title_font_color=fluxcolor,
        secondary_y=False
    )
    # if forced:
    #     fig.update_yaxes(autorange="reversed",secondary_y=True)
    # else:
    #     fig.update_yaxes(autorange="reversed",secondary_y=True,type="log")

    for k in fig.layout:
        if k[:5] ==  'y2axis':
            # print(k)
            fig.layout[k]['range'] = [flux2mag(uffluxMin),flux2mag(uffluxMax)]
            fig.layout[k]['title']['text'] = "Difference Magnitude (AB)"


    # fig.update_yaxes(   # RDW:log right axis
    #     range=[math.log10(flux2mag(uffluxMin)), math.log10(flux2mag(uffluxMax))],  # Inverted range
    #     secondary_y=True,   # right side
    #     showgrid=True,
    #     # tickformat='.3f',
    #     tickfont_size=14,
    #     tickfont_color=magcolor,
    #     tickcolor=magcolor,
    #     ticksuffix=" ",
    #     showline=True,
    #     linewidth=1.5,
    #     linecolor='#1F2937',
    #     ticks='inside',
    #     title_text="Difference Magnitude (AB)",
    #     title_font_size=16,
    #     title_font_color=magcolor,
    #     # overlaying="y",
    #     # tickmode="sync",
    #     type="log"
    # )

    # Add a text box annotation
    fig.add_annotation(
        text=f"uffluxMin = {uffluxMin:.2f} nJy<br>uffluxMax = {uffluxMax:.2f} nJy<br>mag min = {flux2mag(uffluxMin):.2f} mag<br>mag max = {flux2mag(uffluxMax):.2f} mag",
        xref="paper", yref="paper",
        x=0.5, y=1.1,  # Position above the plot
        showarrow=False,
        font=dict(size=14, color="#1F2937"),
        align="center",
        bgcolor="#E6E5E5",
        bordercolor="#1F2937",
        borderwidth=1
    )

    # Create shared y-axis scaling
    # fig.update_yaxes(
    #     range=[uffluxMin, uffluxMax],
    #     tickformat='.0f',
    #     tickfont_size=14,
    #     ticksuffix=" ",
    #     tickfont_color=fluxcolor,
    #     showline=True,
    #     showgrid=True,
    #     linewidth=1.5,
    #     linecolor='#1F2937',
    #     gridcolor='#F0F0F0',
    #     gridwidth=1,
    #     zeroline=True,
    #     zerolinewidth=1.5,
    #     zerolinecolor='#1F2937',
    #     mirror=True,
    #     ticks='inside',
    #     title="Difference Flux (nanoJy)",
    #     title_font_size=14,
    #     title_font_color=fluxcolor,
    #     secondary_y=False,
    #     scaleanchor="y2",
    #     scaleratio=1
    # )
    
    # fig.update_yaxes(   # RDW:log right axis
    #     range=[flux2mag(uffluxMin), flux2mag(uffluxMax)],
    #     secondary_y=True,   # right side
    #     showgrid=False,
    #     tickformat='.1f',
    #     tickfont_size=14,
    #     tickfont_color=magcolor,
    #     tickcolor=magcolor,
    #     ticksuffix=" ",
    #     showline=True,
    #     linewidth=1.5,
    #     linecolor='#1F2937',
    #     ticks='inside',
    #     title_text="Difference Magnitude",
    #     title_font_size=16,
    #     title_font_color=magcolor,
    #     matches='y',
    #     scaleanchor="y",
    #     scaleratio=1
    # )



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
                        args=[{"yaxis.type": "linear", "updatemenus[0].font.color": "#D1D5DB", "updatemenus[0].bgcolor": "#6B7280"}],
                        args2=[{"yaxis.type": "log","updatemenus[0].font.color": "#E11D48", "updatemenus[0].bgcolor": "#D1D5DB"}],
                    ),
                ],
            )
        ]
    )

    fig.add_trace(go.Scatter(
        x=discovery["mjd"],
        y=[uffluxMin*1.05],
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
    else:
        title_text = "Standard Photometry Flux"

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20), y=0.85,
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

    mjdMin = unforcedDF["midpointMjdTai"].min()
    mjdMax = unforcedDF["midpointMjdTai"].max()

    if forcedDF is not None:
        mjdMin2 = forcedDF["midpointMjdTai"].min()
        mjdMax2 = forcedDF["midpointMjdTai"].max()

        if mjdMin2 < mjdMin:
            mjdMin = mjdMin2
        if mjdMax2 > mjdMax:
            mjdMax = mjdMax2

    # SORT BY COLUMN NAME
    discovery = unforcedDF.head(1)
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
    # for the linear plot
    if forcedDF is not None:
        fluxMax = forcedDF.loc[((forcedDF['midpointMjdTai'] > mjdMin) & \
                (forcedDF['midpointMjdTai'] < mjdMax)), "nanojansky"] + forcedDF.loc[((forcedDF['midpointMjdTai'] > mjdMin) & \
                (forcedDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
        fluxMax = fluxMax.max()
        fluxMin = forcedDF.loc[((forcedDF['midpointMjdTai'] > mjdMin) & \
                (forcedDF['midpointMjdTai'] < mjdMax)), "nanojansky"] - forcedDF.loc[((forcedDF['midpointMjdTai'] > mjdMin) & \
                (forcedDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
        fluxMin = fluxMin.min()
        if fluxMin < 0 and fluxMax < 0:
            fluxMax = 0

        yrange = fluxMax - fluxMin
        fluxMax += (yrange * 0.1)
        fluxMin -= (yrange * 0.1)
    else:
        fluxMin, fluxMax = None, None

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    if unforcedDF is not None:
        uffluxMax = unforcedDF.loc[((unforcedDF['midpointMjdTai'] > mjdMin) & \
                (unforcedDF['midpointMjdTai'] < mjdMax)), "nanojansky"] + unforcedDF.loc[((unforcedDF['midpointMjdTai'] > mjdMin) & \
                (unforcedDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
        uffluxMax = uffluxMax.max()
        uffluxMin = unforcedDF.loc[((unforcedDF['midpointMjdTai'] > mjdMin) & \
                (unforcedDF['midpointMjdTai'] < mjdMax)), "nanojansky"] - unforcedDF.loc[((unforcedDF['midpointMjdTai'] > mjdMin) & \
                (unforcedDF['midpointMjdTai'] < mjdMax)), "nanojanskyerr"]
        uffluxMin = uffluxMin.abs().min()
        if uffluxMin < 1: uffluxMin = 1
        if uffluxMax < 0: uffluxMax = 10*abs(uffluxMin)

        uffluxMax *= 1.05
        uffluxMin *= 0.95

    return mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, uffluxMin, uffluxMax

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
