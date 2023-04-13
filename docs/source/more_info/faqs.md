# Questions and Answers

## What are Lasair-ZTF and Lasair-LSST?

See [ZTF and LSST](../about.html#ztf-and-lsst)

## What can I get from this web site?

The Lasair alert broker gives access to millions of astronomical transient detections: when a star or galaxy becomes brighter or fainter than it was at an earlier time.

## What data does Lasair offer?

Whenever a star or galaxy in the sky changes brightness, it is given an "objectId", which can be used to see all the data about that object. Data includes a "light curve" of brightness measurments at different times, in different filters; crossmatching with existing source catalogs, and other data.
Changes in brightness are transferred to the Lasair databases, and pushed to users, within an hour
of the telescope taking the observation.

## What is here for an amateur astronomer?

A serious amateur telescope would have a 500 mm aperture, with a limiting magnitude of about 16, costing over $40,000. In any year there will be a few supenovae visible to this system.

## How can I ask a question to the Lasair team?

Write to the help email: lasair-help at lists.lasair.roe.ac.uk.

## How can I use my knowledge of SQL to use Lasair?

Each filter in Lasair is an SQL SELECT query. The syntax is "SELECT <attributes\> FROM <tables\> WHERE <conditions;\>" The attributes come from the schema -- shown to the right in the filter builder page. The tables are selected from `objects`, `sherlock_classifications`, `crossmatch_tns`, as well as any watchlists, watchmaps or annotations you choose. The conditions in the WHERE clause allow a simplified SQL, using just comparison operators, without operators such as "group" and "having".

## How can I query the Lasair database?

You can type SQL into the filter builder -- [instructions here](../core_functions/make_filter.html), 
and you can run a query somebody else has made that is public. If you sign up and login to Lasair, you can save your queries and you can copy somebody else's query then modify it.

## What is the difference between a Query and a Filter?

A query operates on the whole database of alerts, but a filter only runs on new alerts, as they stream from the telescope. They are very similar ideas: but query implies running on the database of past alerts,
and filter implies running on the stream of incoming new alerts.

## What is the schema of the Lasair database?

Can be found at the [schema page]({%lasairurl%}/schema).

## How do I choose which alerts are interesting to me?

Choosing interesting alerts can be based on several criteria: The characteristics of the light curve; coinicdence of the alert with a galaxy or known variable star; coincidence of the alert with one of the sources in which you are interested (a watchlist); location of the alert in a given area of the sky, for example a gravitational wave skymap.

## Why should I register on the Lasair website?

Registration is easy, and just requires a valid email (signup [here]({%lasairurl%}/signup)). You can then build and save queries, watchlists, and watchmaps (sky areas), convert those to real-time slert treams, and use the Lasair API.

## Besides Lasair, what other websites carry astronommical transients?

There are seven community brokers that will receive and process LSST alerts in real time: [ALeRCE](http://alerce.science/), [AMPEL](https://ampelproject.github.io/), [ANTARES](https://antares.noirlab.edu/), BABAMUL, [Fink](https://fink-broker.re%3Cdthedocs.io/en/latest/), [Lasair](https://lasair.roe.ac.uk/), and [Pitt-Google](https://pitt-broker.re%3Cdthedocs.io/en/latest/).

## How long has Lasair been operating?

Lasair has been processing, storing, and distributing alerts from the ZTF survey since 2018.
Operation with LSST will start in 2023.

## Why are there no alerts on the Lasair front page?

The front page shows alerts from the last seven days. Sometimes no alerts have been received
in that time, and so none are shown. Reasons may be weather or equipment failure.
More information is available in the green news bar at the top of the front page.

## Can I get alerts from a particular region of the sky?

Lasair supports "watchmaps", defined by a [MOC](https://cds-astro.github.io/mocpy/), that you build yourself.

## Can I get alerts associated with my favourite sources?

You can build a "watchlist" of your favourite sources, and build a corresponding query that includes crossmatch with that watchlist. Instructions are [here](../core_functions/watchlists.html).

## Can Lasair alert me about supernovae and kilonovae?

There are some filters already built that find alerts in the outskirts of galaxies. There are also queries that find supernovae already reported to the [Transient Name Service](https://www.wis-tns.org/).

## Can Lasair alert me about gravitational-wave events?

Not yet, but soon.

## How can I find out about the LSST survey and the Vera Rubin Observatory?

General FAQ on LSST and Rubin is [here](https://www.lsst.org/content/rubin-observatory-general-public-faqs), about community alert brokers in particular [here](https://www.lsst.org/scientists/alert-brokers)

## How can I write code and notebooks that use the Lasair database?

The Lasair client is described [here](../core_functions/rest-api.html), and
there are sample notebooks [here](../core_functions/python-notebooks.html).

## Does Lasair classify alerts into classes?

Lasair supports the idea of *annotation*, where external users and other brokers build and
share classification information with Lasair. These annotations can then be used as part of 
Lasair filters.

## Does Lasair have an API?

The Lasair client is described [here](../core_functions/rest-api.html).

## What is difference magnitude compared to apparent magnitude?

This is explained [here](../concepts/objects_sources.html).

## How do search for an object by position in the sky?

This is called a "cone search". See next question.

## What is a cone-search and can Lasair do this?

A *cone* in this context means a point in the sky with an angular tolerance -- the opening
angle of the cone, as explained [here](../concepts/sky-search.html). 
You can use the [Lasair Sky Search](../core_functions/sky-search.html)
to do this.

## How can I do 1000 cone searches all at once?

The efficient way to do this is to build a [watchlist](../concepts/watchlist.html),
as explained [here](../core_functions/watchlist.html). If the watchlist has
less than 10,000 sources, there is button on the watchlist page to crossmatch
with all past objects.

## Can I see sky images in different wavelengths around a Lasair alert?

The Lasair object page has a panel of [AladinLite](https://aladin.u-strasbg.fr/AladinLite/)
that shows many kinds of sky image, from radio to gamma, and can be zoomed in and out.

## When I make a filter, can I share it with my colleagues?

Filters, watchlists, and watchmaps can all be made public so that others can see them.
A public filter can be copied and modified.

## Can I get immediate notification of interesting alerts?

See the section on [alert streams](../core_functions/alert-streams).
