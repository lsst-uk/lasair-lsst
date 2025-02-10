## About Lasair
The [Rubin Observatory](https://www.rubinobservatory.org/)
will provide unprecedented temporal resolution, depth and 
uniform photometry over an entire hemisphere, along with a real-time stream of 
alerts from the ever changing sky. To extract the scientific potential from 
that stream, the community needs brokers that offer the ability to filter, 
query, and manipulate the alerts, and combine them with external data sources. 
The [LSST:UK consortium](https://www.lsst.ac.uk/)
has been building just such a broker [Lasair](http://lasair.lsst.ac.uk), alongside 
an International Data Access Centre (IDAC), building on its strengths and 
heritage in leading astronomical surveys, data processing and analysis. The hope
is that Lasair will be of value to the worldwide community, not just to the the UK consortium.

Please see and cite our paper:
[R.D.Williams et. al., Enabling science from the Rubin alert stream with Lasair](https://doi.org/10.1093/rasti/rzae024), RAS Techniques and Instruments, **3**,1, 362  (2024).

## The Lasair approach
**Lasair is a platform for scientists to make science; it does not try to make 
the science itself.**
Every LSST broker aims to filter the stream, but Lasair does this differently. 
Rather than scientists making python code that needs to be vetted, Lasair 
offers direct access with a staged approach: scientists can start with a 
simple, immediate mechanism using familiar SQL-like languages. These SQL-like 
queries can be custom made or users can choose and modify one of our pre-built 
and tested queries. These queries return an initial selection of objects, based 
on our rich value-added data content, and users can then run their own local 
code on the results. Users can build up to running  their own code on both the 
stream and the database with high-throughput resources in the 
UK science collaboration called [IRIS](https://www.iris.ac.uk/). The 
SQL filters and code can be made public, shared with a group of colleagues, 
copied, and edited.
SQL filters can be escalated from static (run on command) to streaming filters, 
that run whenever new alerts arrive. 

## How Lasair Works
Lasair is built to process transient alerts rapidly and make the key decision: is this an object I want to follow up? LSST alerts will come at very high rate, and Lasair takes advantage of the design of the distribution system: 
["Events are sent in rich alert packets to enable standalone classification"](https://simons.berkeley.edu/sites/default/files/docs/9308/bellmlsst180226.pdf) (slide 48).
Thus alerts are judged based only on that rich alert packet, without database interaction, leading to a very fast processing rate.

The “rich data packet” means a year of past data about each object (or a month for the ZTF prototype). Note that Lasair has the full light curves – available through the object web page or API – but queries and filters are based on these shorter light curves.

See [this page](implementation.html) for a more complete description of how Lasair works.

## Scientific goals of Lasair
Lasair extracts many types of astrophysical phenomena from the alert streams of ZTF/LSST: extragalactic transients, kilonovae and gravitational wave sources, massive samples of supernovae, active galactic nuclei, tidal disruption events, Milky Way and Local Group stellar transients. However, Lasair does not handle Solar System bodies.

See [this page](sciencegoals.html) for a more complete description of science goals.
