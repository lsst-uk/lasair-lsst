import pandas as pd
from astropy.time import Time
import plotly.graph_objects as go
import math, json
import logging
import numpy as np

log = logging.getLogger(__name__)

# THESE ARE THE RUBIN STYLE GUIDE COLOURS AND SYMBOLS
bands  = ['u', 'g', 'r', 'i', 'z', 'y']
bandColors = ['#1600ea', '#31de1f', '#b52626', '#370201', '#ba52ff', '#61a2b3']
bandSymbols = ['circle', 'triangle-up', 'triangle-down', 'square', 'star', 'hexagon']
bandColorsDark = ['#3eb7ff','#30c39f','#ff7e00', '#2af5ff','#a7f9c1','#fdc900']

# HALF-WIDTH OF THE OFFSET SCATTER PLOT AXES, IN ARCSEC
SCATTER_RANGE_ARCSEC = 4.0
# COLOUR FOR A BAND NOT IN THE RUBIN STYLE GUIDE (THE LIGHT CURVE DEFAULT)
UNKNOWN_BAND_COLOR = "#268bd2"
# AXIS, MARKER AND HOVER COLOR OF THE OFFSET SCATTER PLOT
PLOT_LINE_COLOR = "#1F2937"
# ROOM FOR THE NOTES BELOW THE X-AXIS TITLE: PIXELS BELOW THE PLOT AREA, AND THE BOTTOM MARGIN
SCATTER_NOTE_YSHIFT = -50
SCATTER_MARGIN_BOTTOM = 82
# MARGINS AND FIGURE HEIGHT THAT KEEP THE SQUARE PLOT FILLING A THIRD-WIDTH CARD; PLOTLY GROWS THE TOP MARGIN TO FIT THE LEGEND
SCATTER_MARGIN_TOP = 5
SCATTER_MARGIN_LEFT = 50
SCATTER_MARGIN_RIGHT = 15
SCATTER_HEIGHT = 360
# LEGEND POSITION IN PLOT-AREA FRACTIONS: JUST ABOVE THE TOP AXIS, WHICH MAKES PLOTLY GROW THE TOP MARGIN TO FIT IT
SCATTER_LEGEND_Y = 1.02
# MARKER FOR A DETECTION WHOSE BAND IS NOT A RUBIN BAND
UNKNOWN_BAND_SYMBOL = 'circle'
SCATTER_SMALL_FONT_SIZE = 11
# TICK AND AXIS-TITLE STYLE OF THE LIGHT-CURVE AXES (TICKLEN AND TICKWIDTH ARE THE PLOTLY DEFAULTS THE LIGHT CURVE USES)
LIGHTCURVE_AXIS_TICKS = dict(
    ticks="inside",
    ticklen=5,
    tickwidth=1,
    tickfont_size=14,
    title_font_size=14,
)
# LABEL AND TRACE NAME FOR A DETECTION WITH NO BAND
UNKNOWN_BAND_LABEL = "unknown"
ARCSEC_PER_DEGREE = 3600.0

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
    
    if forced and forcedDF is None:
        return None, None

    if forced:
        lcDF = forcedDF 
    else:
        lcDF = unforcedDF

    

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin, mjdMax, utcMin, utcMax, fluxMin, fluxMax, magMin, magMax = get_default_axis_ranges(lcDF)

    # DEFAULT DATA FRAME
    lcDF["marker_color"] = UNKNOWN_BAND_COLOR
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
#                    x=data["mjd"],   # no mjd for forced phot 
                    x=data["midpointMjdTai"],
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
#                    x=data["mjd"],   # no mjd for forced phot 
                    x=data["midpointMjdTai"],
                    y=data["nanojansky"],
                    customdata=np.stack((data['utc'], data['nanojansky'], data['magpsf']), axis=-1),
                    mode='markers',
                    marker_size=data["marker_size"].values[0],
                    marker_color=UNKNOWN_BAND_COLOR,
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
                go.Scatter(x=data["midpointMjdTai"],   # no mjd for forced
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

    # Define the tick values for the secondary y-axis
    rangeDays = int(mjdMax - mjdMin)
    # NUMPY ARRAY FROM 10 to 100 in steps of 2
    steps = int(rangeDays/5)
    tickvals = np.arange(int(mjdMin)-rangeDays*5, int(mjdMax)+rangeDays*5,  steps)
    

    # Convert tick values to the desired format
    mjd2utc = Time(tickvals, format='mjd')
    from datetime import datetime
    ticktext = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d') for time in mjd2utc.iso]

    adjustTopTitle = round(len(allDataSets)/2)-4
    if adjustTopTitle > 0:
        adjustTopTitle = adjustTopTitle * 0.05
    else:
        adjustTopTitle = 0

    fig.update_layout(
        annotations=[
            dict(
                xref="paper",
                yref="paper",
                x=0.5+adjustTopTitle,  # Adjust x position (0=left, 1=right of plot area)
                y=1.22, # Adjust y position (relative to plot area)
                text=ttitle,
                showarrow=False,
                xanchor="right", 
                yanchor="top",
                font_size=ttitle_font_size,
            )
        ]
    )

    


    fig.update_layout(  
        xaxis=dict(
            side="bottom",
            range=[mjdMin, mjdMax],
            tickformat='d',
            tickangle=-25,
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
            title=dict(
                text=btitle
            ),
            title_font_size=btitle_font_size,
            tickvals=tickvals,  # Original tick values
        ),
        xaxis2=dict(
            title=dict(
                text=""
            ),
            title_font_size=ttitle_font_size,
            tickfont_size=ttickfont_size,
            side="top",
            overlaying="x", # Overlay on the first x-axis
            matches="x",  # Keep the two x-axes in sync
            range=[mjdMin, mjdMax],
            tickangle=-25,
            ticks='inside',
            showline=True,
            linewidth=1.5,
            linecolor='#1F2937',
            gridcolor='#F0F0F0',  # Add grid color
            gridwidth=1,          # Add grid width
            tickvals=tickvals,  # Original tick values
            ticktext=ticktext,    # Converted tick labels
        )
    )

    # Define the tick values for the secondary y-axis
    rangeFlux = fluxMax - fluxMin

    # round value of step for any range
    def roundme(f, down=True):
        if f < 0.0:
            return -roundme(-f, down=not down)
        (fr, ir) = math.modf(math.log10(f))
        pow10 = math.pow(10.0, ir)
        fac   = math.pow(10.0, fr)
        if down:
            if   fac > 5: rnd = 5*pow10
            elif fac > 2: rnd = 2*pow10
            else:         rnd =   pow10
        else:
            if   fac > 5: rnd =10*pow10
            elif fac > 2: rnd = 5*pow10
            else:         rnd = 2*pow10
        return rnd

    fluxMinRounded = roundme(fluxMin,  down=True)
    fluxMaxRounded = roundme(fluxMax,  down=False)
    step =       0.1*roundme(rangeFlux,down=False)
    tickvals = np.arange(fluxMinRounded, fluxMaxRounded,  step)

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
        tickvals=tickvals,  # Original tick values

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
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        ticks='inside',
        title_text="Difference Magnitude (AB)",
        title_font_size=14,
        title_font_color=magcolor,
        tickvals=tickvals,  # Original tick values
        ticktext=ticktext,    # Converted tick labels
        overlaying="y",
        matches="y"  # Keep the two y-axes in sync
    )


    if forced:
        title_text = " Forced Photometry"
        margin_t = 100
        y = 1.2
    else:
        title_text = " Standard Photometry"
        margin_t = 0
        y = 1.25


    # UPDATE PLOT LAYOUT
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=550+margin_t,
        margin_t=margin_t,
        margin_b=0,
        margin_r=1,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=y,
            xanchor="left",
            x=0.0,
            bgcolor="#E6E5E5",
            borderwidth=4,
            bordercolor="#E6E5E5",
            title=title_text
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



    htmlLightcurve = fig.to_html(
        config={
            'displayModeBar': False,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'filename': objectData["diaObjectId"] + "_lasair_lc"},
            'responsive': True
        })

    return htmlLightcurve, mergedDF

def compute_source_offsets(
        objectRa,
        objectDec,
        sources):
    """*compute the tangent-plane offset of each source from the object position*

    **Key Arguments:**

    - ``objectRa`` -- the mean RA of the object in degrees
    - ``objectDec`` -- the mean Dec of the object in degrees
    - ``sources`` -- a list of diaSource dictionaries (``diaSourceId``, ``ra``, ``decl``, ``band``, ``midpointMjdTai``)

    **Return:**

    - ``offsets`` -- a list of dictionaries with keys ``diaSourceId``, ``mjd``, ``band`` (``unknown`` if missing or not a Rubin band), ``dRa`` (arcsec, scaled by cos(Dec)) and ``dDec`` (arcsec); sources whose ra or decl is missing, non-numeric or non-finite are left out, so ``len(sources) - len(offsets)`` is their count

    **Usage:**

    ```python
    offsets = compute_source_offsets(data["objectData"]["ra"], data["objectData"]["decl"], data["diaSources"])
    ```
    """
    cosDec = math.cos(math.radians(objectDec))
    offsets = []
    for source in sources:
        ra = to_finite_float(source.get("ra"))
        decl = to_finite_float(source.get("decl"))
        if ra is None or decl is None:
            continue
        band = source.get("band")
        # WRAP THE RA DIFFERENCE INTO [-180, 180) SO 359.9999 -> 0.0001 IS A SMALL STEP
        deltaRa = (ra - objectRa + 180.0) % 360.0 - 180.0
        offsets.append({
            "diaSourceId": source.get("diaSourceId"),
            "mjd": to_finite_float(source.get("midpointMjdTai")),
            # ONLY THE RUBIN BANDS GET THEIR OWN TRACE, SO MALFORMED DATA CANNOT CREATE MANY TRACES
            "band": str(band) if band is not None and str(band) in bands else UNKNOWN_BAND_LABEL,
            "dRa": deltaRa * cosDec * ARCSEC_PER_DEGREE,
            "dDec": (decl - objectDec) * ARCSEC_PER_DEGREE,
        })
    return offsets


def to_finite_float(
        value):
    """*convert a value to a finite float*

    **Key Arguments:**

    - ``value`` -- the value to convert, such as a number, a numeric string or None

    **Return:**

    - ``number`` -- the value as a float, or None if it is missing, non-numeric, NaN or infinite

    **Usage:**

    ```python
    ra = to_finite_float(source.get("ra"))
    ```
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def is_offset_in_range(
        offset,
        limit=SCATTER_RANGE_ARCSEC):
    """*test whether an offset lies inside the square plot range*

    **Key Arguments:**

    - ``offset`` -- an offset dictionary from ``compute_source_offsets``
    - ``limit`` -- the half-width of the plot range in arcsec

    **Return:**

    - ``isInRange`` -- True if both offsets are within ``limit``

    **Usage:**

    ```python
    isInRange = is_offset_in_range({"dRa": 1.0, "dDec": -2.0})
    ```
    """
    return abs(offset["dRa"]) <= limit and abs(offset["dDec"]) <= limit


def split_offsets_by_range(
        offsets,
        limit=SCATTER_RANGE_ARCSEC):
    """*split offsets into those inside and outside the square plot range in one pass*

    **Key Arguments:**

    - ``offsets`` -- a list of offset dictionaries from ``compute_source_offsets``
    - ``limit`` -- the half-width of the plot range in arcsec

    **Return:**

    - ``inRange`` -- the offsets within ``limit`` on both axes
    - ``outsideRange`` -- the offsets beyond ``limit`` on either axis

    **Usage:**

    ```python
    inRange, outsideRange = split_offsets_by_range(offsets)
    ```
    """
    inRange, outsideRange = [], []
    for offset in offsets:
        (inRange if is_offset_in_range(offset, limit) else outsideRange).append(offset)
    return inRange, outsideRange


def build_offset_scatter_notes(
        outsideCount,
        noPositionCount):
    """*build the notes that tell the reader which detections are not plotted*

    **Key Arguments:**

    - ``outsideCount`` -- the number of detections beyond the plot range
    - ``noPositionCount`` -- the number of detections with no position

    **Return:**

    - ``notes`` -- a list of note strings, empty when every detection is plotted

    **Usage:**

    ```python
    notes = build_offset_scatter_notes(2, 0)
    ```
    """
    notes = []
    if outsideCount:
        noun = "detection" if outsideCount == 1 else "detections"
        notes.append("%d %s outside plot range" % (outsideCount, noun))
    if noPositionCount:
        noun = "detection" if noPositionCount == 1 else "detections"
        notes.append("%d %s without a position" % (noPositionCount, noun))
    return notes


def build_offset_scatter_figure(
        objectData):
    """*build the Plotly figure of detection offsets from the object position*

    **Key Arguments:**

    - ``objectData`` -- the object data (uses ``objectData.ra``, ``objectData.decl`` and ``diaSources``; forced photometry is ignored)

    **Return:**

    - ``fig`` -- the Plotly figure, or None if the object has no detections or no usable position
    - ``outsideCount`` -- the number of detections beyond the plot range

    **Usage:**

    ```python
    fig, outsideCount = build_offset_scatter_figure(data)
    ```
    """
    sources = objectData.get("diaSources")
    position = objectData.get("objectData") or {}
    objectRa = to_finite_float(position.get("ra"))
    objectDec = to_finite_float(position.get("decl"))
    if not sources or objectRa is None or objectDec is None:
        return None, 0

    offsets = compute_source_offsets(objectRa, objectDec, sources)
    inRange, outsideRange = split_offsets_by_range(offsets)
    notes = build_offset_scatter_notes(len(outsideRange), len(sources) - len(offsets))

    fig = go.Figure()
    for trace in make_offset_band_traces(inRange):
        fig.add_trace(trace)
    fig.add_trace(make_origin_trace())
    apply_offset_scatter_layout(fig)
    if notes:
        # THE NOTE SITS BELOW THE X-AXIS TITLE, IN THE BOTTOM MARGIN
        fig.add_annotation(
            xref="paper", yref="paper", x=0.5, y=0, yshift=SCATTER_NOTE_YSHIFT,
            text="<br>".join(notes),
            showarrow=False, xanchor="center", yanchor="top", font_size=SCATTER_SMALL_FONT_SIZE,
        )
    return fig, len(outsideRange)


def make_offset_band_traces(
        offsets):
    """*make one marker trace per band, colored as in the light curve*

    **Key Arguments:**

    - ``offsets`` -- a list of offset dictionaries from ``compute_source_offsets``

    **Return:**

    - ``traces`` -- a list of Plotly scatter traces, known bands first in light curve order

    **Usage:**

    ```python
    traces = make_offset_band_traces(inRange)
    ```
    """
    colorByBand = dict(zip(bands, bandColors))
    symbolByBand = dict(zip(bands, bandSymbols))
    presentBands = {offset["band"] for offset in offsets}
    traces = []
    # KNOWN BANDS FIRST, IN LIGHT CURVE ORDER, THEN ANY OTHERS
    for band in bands + sorted(presentBands - set(bands)):
        bandOffsets = [offset for offset in offsets if offset["band"] == band]
        if not bandOffsets:
            continue
        traces.append(go.Scatter(
            x=[offset["dRa"] for offset in bandOffsets],
            y=[offset["dDec"] for offset in bandOffsets],
            customdata=[
                [str(offset["diaSourceId"]) if offset["diaSourceId"] is not None else "unknown", offset["mjd"], offset["band"]]
                for offset in bandOffsets],
            mode="markers",
            marker_color=colorByBand.get(band, UNKNOWN_BAND_COLOR),
            marker_symbol=symbolByBand.get(band, UNKNOWN_BAND_SYMBOL),
            marker_size=9,
            marker_opacity=0.7,
            name=band + "-band",
            showlegend=True,
            hovertemplate="<b>diaSourceId: %{customdata[0]}</b><br>" +
                "MJD: %{customdata[1]:.5f}<br>" +
                "Band: %{customdata[2]}<br>" +
                "ΔRA×cos(Dec): %{x:.3f} arcsec<br>" +
                "ΔDec: %{y:.3f} arcsec" +
                "<extra></extra>",
        ))
    return traces


def make_origin_trace():
    """*make the trace that marks the object mean position at (0, 0)*

    **Return:**

    - ``trace`` -- a Plotly scatter trace with one marker and no legend entry

    **Usage:**

    ```python
    fig.add_trace(make_origin_trace())
    ```
    """
    return go.Scatter(
        x=[0],
        y=[0],
        mode="markers",
        marker_symbol="cross-thin-open",
        marker_color=PLOT_LINE_COLOR,
        marker_size=14,
        marker_line_width=2,
        showlegend=False,
        hoverinfo="skip",
    )


def apply_offset_scatter_layout(
        fig):
    """*apply the fixed-range, equal-aspect light theme layout to the offset scatter figure*

    **Key Arguments:**

    - ``fig`` -- the Plotly figure to style in place

    **Usage:**

    ```python
    apply_offset_scatter_layout(fig)
    ```
    """
    limit = SCATTER_RANGE_ARCSEC
    axisStyle = dict(
        showline=True,
        linewidth=1.5,
        linecolor=PLOT_LINE_COLOR,
        gridcolor="#F0F0F0",
        zeroline=False,
        **LIGHTCURVE_AXIS_TICKS,
        # KEEP THE RANGE AT +/- THE LIMIT AND SHRINK THE PLOT AREA TO STAY SQUARE
        constrain="domain",
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=SCATTER_HEIGHT,
        margin_t=SCATTER_MARGIN_TOP,
        margin_b=SCATTER_MARGIN_BOTTOM,
        margin_l=SCATTER_MARGIN_LEFT,
        margin_r=SCATTER_MARGIN_RIGHT,
        showlegend=True,
        # RA INCREASES TO THE EAST, WHICH IS ON THE LEFT OF THE SKY, SO THE X RANGE IS DISPLAYED REVERSED
        xaxis=dict(title_text="ΔRA × cos(Dec) (arcsec)", range=[limit, -limit], **axisStyle),
        yaxis=dict(title_text="ΔDec (arcsec)", range=[-limit, limit], scaleanchor="x", scaleratio=1, **axisStyle),
        # ABOVE THE PLOT, OUTSIDE THE AXES, SO IT NEVER COVERS A DETECTION
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=SCATTER_LEGEND_Y,
            xanchor="center",
            x=0.5,
            bgcolor="#E6E5E5",
            borderwidth=4,
            bordercolor="#E6E5E5",
            font_size=SCATTER_SMALL_FONT_SIZE,
        ),
        hoverlabel=dict(font_color="white", bgcolor=PLOT_LINE_COLOR, font_size=14),
    )


def object_offset_scatter(
        objectData):
    """*Generate the Plotly figure of detection offsets from the object position, as plain data*

    The object page passes the result to the ``json_script`` template filter and draws it with
    ``Plotly.newPlot`` once the page has loaded, so the card can sit above the light curve that
    loads plotly.js.

    **Key Arguments:**

    - ``objectData`` -- a json object containing the object position and its diaSources

    **Return:**

    - ``figureSpec`` -- a dictionary with the Plotly ``data`` and ``layout``, or None if the object has no detections

    **Usage:**

    ```python
    from lasair.apps.object.utils import object_offset_scatter
    figureSpec = object_offset_scatter(data)
    ```
    """
    fig, _ = build_offset_scatter_figure(objectData)
    if fig is None:
        return None

    # ROUND-TRIP THROUGH PLOTLY'S ENCODER SO NUMPY VALUES BECOME PLAIN JSON TYPES
    figureSpec = json.loads(fig.to_json())
    return {"data": figureSpec["data"], "layout": figureSpec["layout"]}

def object_offset_scatter_or_none(
        objectData):
    """*generate the offset scatter figure, returning None instead of raising*

    The scatter is an optional card, so a failure here must never break the object page.

    **Key Arguments:**

    - ``objectData`` -- a json object containing the object position and its diaSources

    **Return:**

    - ``figureSpec`` -- the Plotly ``data`` and ``layout`` dictionary, or None if there is nothing to plot or plotting failed (the failure is logged)

    **Usage:**

    ```python
    offsetScatterFigure = object_offset_scatter_or_none(data)
    ```
    """
    try:
        return object_offset_scatter(objectData)
    except Exception:
        log.exception("Failed to build the offset scatter plot")
        return None


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
