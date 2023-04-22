## Quick Start
Lasair is built as a platform to enable scientific discoveries from the dynamic 
Universe.  Its input is a transient sky survey such as ZTF or LSST, that find changes in 
brightness in the night sky, each called an "alert". Such alerts may result 
from supernovae, active galaxies, merging neutron stars, variable stars, and many other 
astrophysical phenomena (see [here](about.html#extragalactic-transients) for more). 

Alerts from the same place in the sky are combined to 
[objects](concepts/objects_sources.html).
The alerts provide the brightness of the object with time -- 
see [here](concepts/lightcurve.html) for more. 
Lasair adds information to the object, matching the position with the known 
astronomical catalogs -- see [here](concepts/sky-context.html).

The transient surveys provide large numbers of alerts: about 400,000 per night 
from ZTF when the sky is clear at Palomar in California, rising to millions per 
night when the [Rubin Observatory](https://www.lsst.org/) in Chile
is running its flagship LSST survey. Far too many for a human to consider! 
Therefore the primary duty of a broker like Lasair is to *filter* the stream to 
concentrate what is wanted and discard that which is not. In this section 
we show **how to make a Lasair filter**,
specifically the one used for building the set of alerts shown on the 
[Lasair front page]({%lasairurl%}/). That display is made from recent, bright, 
real alerts that are identified with known classes of stars and galaxies. 
If you click on any of the red, orange, blue, or yellor markers, you will see 
a popup witha link to the full object page, the age of the most recent alert, 
its magnitude, and its class.

Each object in the Lasair objects table has a lot of columns in several tables, 
and for this example we will concentrate on just a few:

* From the objects table:
    * `objectId`: The identifier for an object that is used to link to the full 
object page,
    * `ramean, decmean`: The position of the object in the sky, to place it 
correctly,
    * `gmag, rmag`: the magnitudes of the latest alert in the g and r filters,
    * `jdmax`: the Julian Day (i.e.date and time) of the latest alert,
    * `jdnow()`: an SQL function that returns the Julian Day now, so we can 
subtract to get the age in days,
    * `ncandgp`: number of good, positive alerts belonging to this object. 
* From the sherlock_classifications table:
    * `classification`: Sherlock class according to the sky context -- see 
[core_functions/sherlock.html](here) for more.

### Create New Filter
We can build the filter by clicking on 'Filters' in the Lasair sidebar, then 
the red button 'Create New' at top right.

For your first filter, you won't be using any of the dropdowns for Watchlist, 
Watchmap, or Object Annotators, you'll fill in the black textarea labelled 
**SELECT COLUMNS** and **WHERE**. 

Type the black lines below in the SELECT COLUMNS.
```
objects.objectId,
```
Notice that as you type, the intelligent autocomplete makes suggestions.  Don't forget the comma at the end.
```
objects.ramean, objects.decmean,
```
The word *mean* is because this is the average position of the multiple alerts that are part of the same object. Don't forget the comma at the end.
```
objects.gmag, objects.rmag,
```
The g or r magnitude for the most recent alert. Each alert is done with one of the filters, so either `gmag` or `rmag` will be `NULL`.
```
jdnow()-objects.jdmax AS age,
```
This SQL fragment subtracts the Julian Day now from the Julian Day of the alert, and renames the result as `age`.
```
sherlock_classifications.classification AS class
```
This attribute is from a different table, the Sherlock classification of the object. The long name is renamed as the much simpler `class`.

You see as you type that the tables you are using appear in the middle of the 
three black textareas, labelled **FROM**.

Now type these lines into the **WHERE** box:
```
objects.jdmax > jdnow() - 7
```

We select only those objects whose most recent alert has been in the last 7 days.
```
AND (objects.gmag < 17 OR objects.rmag < 17)
```

We want bright objects only, mostly to cut the numbers being drawn on the Lasair front page. Give that one of the attributes is `NULL` the `OR` selects the one that is not, and requires it to be less than 17. Don't forget the `AND` at the beginning.
```
AND objects.ncandgp > 1
```

There are a lot of 'orphans' in the Lasair database, that have only one alert. Many of these are not worth looking at, so we require the number of candidates to be greater than 1.
```
AND sherlock_classifications.classification in ("SN", "NT", "CV", "AGN")
```
These codes are for the different Sherlock classifications: possible supernova, nuclear transient cataclysmic variable, active galaxy.

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

Click the black button 'Save' on the create fulter page, then fill in the 
details: Name and Description, and you can choose to make it public, so that it 
appears in the [Public Gallery](({%lasairurl%}/filters). Once its shared like 
this, others can use it, or copy and modify it. Another option in the Save 
dialogue 
has three choices:
* muted: The filter is saved, and you can run it and edit it
* email stream (daily): Means that you receive an email -- at the address of 
your Lasair account -- 
whenever an alert causes an object to pass through the filter. 
This is restricted to one email in 24 hours.
* kafka stream: The substream induced by the filter becomes a kafka stream -- 
see [here](core_functions/alert-streams.html) for more.

Other options on the filter page bring in other tables in addition to the
`objects` table 
-- see [the schema browser]({%lasairurl%}/schema) for the full list. These 
include:

* `sherlock_classifications`: the results of an intelligent matching of 
multiple catalogues 
with the position of the alert on the sky -- see 
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
