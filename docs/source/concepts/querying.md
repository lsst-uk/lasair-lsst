# Queries and Filters

Lasair attempts to blur the line between a *select query* and a *streaming filter*.

## Select Query

The select query can be initiated through the Lasair web, or by using the Lasair API; 
it has a `SELECT` clause and a `WHERE` clause that are entered separately, the first being 
what is reported back and the second the criteria. There is also a choice of which data sources
to choose from in addition to the `object` table.

If I choose my own watchlist in addition to the `object` table, and the `SELECT` clause is 
```
objects.objectId, watchlist_hits.name, objects.glatmean
```
and there the `WHERE` clause is 
```
glatmean > 20
ORDER BY glatmean
```
and I click 'Run this Query', then I get a list of objects that are coincident with
the given watchlist, together with the watchlist's name, and the galactiv latitude.
The `WHERE` clause has restricted the results by galactic latitude, and the results
come in order of galactic latitude.

## Multiple Tables

Lasair supports queries that join multiple tables, for example a watchlist of 
your favourite sources, or the [TNS](https://www.wis-tns.org/) list of known 
supernovae and other transients. In this case, you are selecting **ONLY** those
objects that are **ALSO* in the chosen table. If you make a filter that selects 
```objectId``` and you also choose a watchlist, then your filter returns only alerts
coincident with the sources in the watchlist. 

## Streaming Filter

The query-building page has a checkbox that changes a saved query to a filter, meaning that 
whenever an incoming alert satisfies the criteria, a message is sent to the user of that
query. The message can be via email (with messages bundled into a 24-hour digest), or it 
can be machine-readable by a Kafka stream. In this way, a user -- or their machine -- can be
alerted in near-real-time, withing minutes of the telescope taking the data. This message is
repeated whenever new data comes in; in the example above, a message wouyld be generated every
time an alert coincides with the watchlist and has `glatmean > 20`.

However, the results of a streaming filter are not identical to running the same stored 
query from web or API. As noted above, a given object can be reported multiple times when
the streaming filter is operating, but only once in the select query. The other difference
is that the ordering of results from a streaming filter will *always* by time order, so the 
`ORDER BY` part of the `WHERE` clause is ignored.

## Cookbook

For instructions on how to make a filter, see [Make a Lasair Filter](../core_functions/make_filter.html).
