## Quick Start
Lasair is built as a platform to enable scientific discoveries from the dynamic 
Universe.  Its input is a transient survey, that finds significant changes of 
brightness of object in the night sky, each called an "alert". Such alerts may result 
from supernovae, active galaxies, merging neutron stars, variable stars, and many other 
astrophysical phenomena (see [here](about.html) for more). 

Alerts from the same place in the sky are combined to 
[objects](concepts/objects_sources.html).
The alerts provide the brightness of the object with time -- 
see the [lightcurve discussion](concepts/lightcurve.html) for more. 
Lasair adds information to the object, matching the position with the known 
astronomical catalogs -- see [here](concepts/sky-context.html).

There may be millions of alerts per
night when the [Rubin Observatory](https://www.lsst.org/) in Chile
is running its flagship LSST survey. Far too many for a human to consider! 
Therefore the primary duty of a broker like Lasair is to *filter* the stream to 
concentrate what is wanted and discard that which is not. In this section 
we show **how to make a Lasair filter**,
specifically the one used for building the set of alerts shown on the 
[Lasair front page]({%lasairurl%}/). That display is made from recent, bright, 
real alerts that are identified with known classes of stars and galaxies. 
If you click on any of the red, orange, blue, or yellow markers, you will see 
a popup with a link to the full object page, the age of the most recent alert, 
its magnitude, and its class.

To get started we will focus on a few properties (columns) of a Lasair object recorded in two of the most commonly used tables:

* From the objects table:
    * `diaObjectId`: The identifier for an object that is used to link to the full 
object page,
    * `ra, decl`: The position of the object in the sky, in decimal degrees, to place it correctly,
    * `lastDiaSourceMJD`: the Modified Julian Day (i.e.date and time) of the latest alert,
    * `tainow()`: an SQL function that returns the MJD now, so we can 
subtract to get the age in days,
    * `nSources`: number of alerts belonging to this object. 
* From the sherlock_classifications table:
    * `classification`: [Sherlock class](core_functions/sherlock.html) according to the sky context.

### Create New Filter
We can build the filter by clicking on 'Filters' in the Lasair sidebar, then 
the red button 'Create New' at top right.

For your first filter, you won't be using any of the dropdowns for Watchlist, 
Watchmap, or Object Annotators, you'll fill in the black text areas labelled 
**SELECT COLUMNS** and **WHERE**. 

Type the black lines below in the SELECT COLUMNS.
```
objects.diaObjectId,
```
Notice that as you type, the intelligent autocomplete makes suggestions. It will add a comma as well,
even though the last attribute should not have a comma. Here is the position of the object:
```
objects.ra, objects.decl,
```
Next is the time since the object was last observed. Notice the arithmetic and renaming 
that is part of the SQL language:
```
tainow()-objects.lastDiaSourceMJD AS age,
```
This attribute is from a different table, the Sherlock classification of the object. 
The long name is renamed as the much simpler `class`.
```
sherlock_classifications.classification AS class
```

You see as you type that the tables you are using appear in the middle of the 
three black text areas, labelled **FROM**.

We select only those objects whose most recent alert has been in the last 7 days.
Type these lines into the **WHERE** box:
```
tainow() - objects.lastDiaSourceMJD < 7
```
We want bright objects only, mostly to cut the numbers being drawn on the Lasair front page. 
A flux of 100,000 nanoJanskies is about magnitude 19.
Don't forget the `AND` at the beginning.
```
AND (objects.g_psfFlux > 100000 OR objects.r_psfFlux > 100000)
```
There are a lot of 'orphans' in the Lasair database, meaning objects that have only one candidate (detection). Many of these are not worth looking at, so we require the number of candidates to be greater than 1.
```
AND objects.nSources > 1
```
Finally, lets choose objects that have an associated host galaxy. These codes are for the different Sherlock classifications: possible supernova, nuclear transient cataclysmic variable, active galaxy.
```
AND sherlock_classifications.classification in ("SN", "NT", "CV", "AGN")
```

### Run your filter
You can simply run the filter on the existing database by clicking the red 
button 'Run Filter'.
You should see a table of the recent alerts, the same set as are on the Lasair 
front page.
You can click on the column headers to sort, and click on the `objectId` to go 
to the detail 
for any of the objects.

### Save your filter
But doing more with Lasair requires an account -- its just a simple matter of 
entering
your valid email address -- see [here to register]({%lasairurl%}/register).

Click the black button 'Save' on the create filter page, then fill in the 
details: Name and Description, and you can choose to make it public, so that it 
appears in the [Public Gallery]({%lasairurl%}/filters). Once its shared like 
this, others can use it, or copy and modify it. Another option in the Save 
dialogue has three choices:

* muted: The filter is saved, and you can run it and edit it
* email stream (daily): Means that you receive an email -- at the address of 
your Lasair account -- 
whenever an alert causes an object to pass through the filter. 
This is restricted to one email in 24 hours.
* kafka stream: The substream induced by the filter becomes a 
[kafka stream](core_functions/alert-streams.html).

Other options on the filter page bring in other tables in addition to the
`objects` table 
-- see [the schema browser]({%lasairurl%}/schema) for the full list. These 
include:

* `sherlock_classifications`: the results of an intelligent matching of 
multiple catalogues with the position of the alert on the sky -- see 
[here](core_functions/sherlock.html) for more.
* `crossmatch_tns`: you can filter your results to be alerts coincident with the 
[TNS](https://www.wis-tns.org/) name server. You can select supernova types , 
dscovery date, and more.
* `watchlist`: you can filter your results to be only those coincident with a 
list of sources that you or someone else has  uploaded -- see 
[here](core_functions/watchlists.html) for more.
* `watchmap`: you can filter your results to be only those inside a sky area 
that you or someone else has uploaded -- see [here](core_functions/watchmaps.html) for more.
* `annotation`: you can find events that have been classified or otherwise 
annotated external to Lasair. You can also set up your own annotation service -- see 
[here](concepts/annotations.html).

### Lasair client and notebooks
Once you can build a filter with the web pages, you might want to run with python code instead of clicks.
There is a client library for Lasair with methods for positional search, 
running queries on the Lasair database, and other functions -- see 
[here](core_functions/client.html). There is also a set of Jupyter notebooks illustrating use of the client [here](core_functions/python_notebooks.html).

### Kafka and Annotation
Once you have a filter that produces the alerts you want, you might want to have your machine receive them and act on your behalf. This is explained [here](core_functions/alert-streams.html).

You can add information to the Lasair database, with your own classification algorithm or other added value. This in the annotation process: see [here](core_functions/alert-streams.html) for more information.
