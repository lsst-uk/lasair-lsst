## How Lasair Works
Lasair runs in the Somerville computing cloud at the Advanced Computing Facility 
near Edinburgh, Scotland. 

<img src="_images/Architecture.png" width="700px"/>

Lasair ingests data with a pipeline of clusters: each cluster does a different 
job, some more compute/data intensive than others, so it is difficult to know a 
priori how much resource should be allocated to each. Our design gives 
flexibility: each cluster can be grown or reduced according to need. Also, 
there are various persistent data stores, again, each is driven by a resilient 
cluster that can be grown or reduced according to need. The diagram shows the 
concept: data enters the Kafka system on the left and progresses to the right. 
The green cluster reads, processes, and puts different data into the Kafka bus; 
as soon as that starts the yellow cluster pulls and pushes; eventually the 
whole pipeline is working. The clusters may also be reading and writing the 
data stores.
We also include the web and annotator nodes in this picture (bottom and right), 
as well as the mining nodes, although they are not part of the data ingestion 
pipeline. The web server nodes support users by delivering web pages and 
responding to API requests. The annotator nodes may be far from the Lasair 
computing centre and not controlled by us, but they are in this picture because 
just like the others, they push data into the data storage and may read from 
Kafka.

The Kafka system is represented by the green nodes in the diagram as well as the 
grey arrow at the top. It is responsible for reading and caching the alert 
packets from the USA, as well as sending it to the compute nodes and receiving 
their resulting packets.

The Ingest nodes read the original alerts alerts from the Kafka system, and 
puts the cutout images in the shared filesystem, the recent lightcurve to NoSQL 
(Cassandra) database, then reformats the alert as JSON – since there is no 
binary content – then pushes that into the Kafka system. 

Each Sherlock node has a SQL database of 5 Tbytes of astronomical sources from 
~40 catalogues. The sky position of the input alert is used to intelligently 
decide on the most likely associated source from the catalogues, finding out, 
for example, if the alert is associated with a known galaxy, or if the alert is 
a flare from a known CV (cataclysmic variable). 

Each filter node computes features of the 30-day light curve that comes with 
the alert (a year with LSST), as well as matching the alert against user-made 
watchlists and areas. Records are writen to a local SQL database onboard the 
node for the object and features, the Sherlock data, the watchlist and area 
tags. Other tables have already been copied into the local database from the 
main SQL database (see Background Services below). After a batch of perhaps 
10,000 alerts are ingested to the local database, it can now execute the 
user-made queries and push out results via the public Kafka system – or via 
email if the user has chosen this option. **NOTE** User-made queries have a time-out 
of 10 seconds, so they can't hold up the entire system if they are too resource intensive.
Usually, however, a user query will execute in a second or less since there are only 10,000
objects in the local database.

The tables in the local database are 
then pushed to the main SQL database and replace any earlier information where 
and object is already known. Once a batch is finished, the local database 
tables are truncated and a new batch started.

The Lasair webserver and API server allow users to control their interactions 
with the alert database and the stream. They can create a watchlist of their 
interesting sources, and Lasair will report crossmatches with members of the 
watchlist. They can define regions of the sky, and Lasair will report when 
alerts fall inside a region. They can define and save SQL queries that can run 
in real time as filters on the alert stream.

The Lasair API supports annotation: a structured external packet of extra 
information about a given object, that is stored in the annotations table in 
the SQL database. This could be, the result of running a machine-learning 
algorithm on the lightcurve, the classification created by another broker, or 
data from a follow-up observation on the object, for example a link to a 
spectrum. Users that put annotations into the Lasair database are vetted, and 
administrators then make it possible. That user will run a method in the Lasair 
API that pushes the annotation: all this can be automated, meaning the 
annotation may arrive within minutes of the observation that triggers it.

## ZTF and LSST
The Lasair project splits into two: the existing working version, Lasair-ZTF, 
that has been ingesting and exposing alerts from the ZTF survey for two years; 
and the future version Lasair-LSST, which is being developed based on the 
lessons learned from Lasair-ZTF. We are keeping the essentials of the user 
interface of Lasair-ZTF (static and streaming SQL queries, full database 
access, watchlists, classification and annotation), but are rebuilding the 
backend architecture for LSST event rates, using parallel services and scalable 
software.

In the timeframe beyond the first data releases of LSST, we can expect 
continuing change. New surveys will come on line, new robotic follow-up 
systems, and new classification systems will proliferate, leading to more 
real-time transient streams and derived information. Just as cross-matching of 
static catalogues has gained importance in the last years, so *dynamic* 
cross-matching will become an engine of discovery: those transients observed by 
A and B, or classified in contradiction by C and D. While the bulk of data will 
continue to be dominated by Rubin data, there will be a deluge of metadata and 
annotation. Lasair will be well-suited to this challenge, building on our existing 
mechanisms for dynamic cross-match (e.g. the IAU's Transient Name Server) and 
utilising our flexible schema system. Lasair will add new tables and schemas to 
our databases, and build information systems to make it easy for scientists to 
navigate the deluge of metadata.

## Decisions from the Alert Packet
Lasair is built to process transient alerts rapidly and make the key decision: is this an object I want to follow up? LSST alerts will come at very high rate, and Lasair takes advantage of the design of the distribution system: ["Events are sent in rich alert packets to enable standalone classification"](https://simons.berkeley.edu/sites/default/files/docs/9308/bellmlsst180226.pdf). Thus alerts are judged based only on that rich alert packet, without database interaction, leading to a very fast processing rate.

The "rich data packet" means a year of past data about each object (or a month for the ZTF prototype). Note that Lasair has the full light curves -- available through the object web page or API -- but queries and filters are based on these shorter light curves.

We note that the calibrated ZTF data releases are [hosted at Caltech](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html) and the LSST archives will hosted by [LSST:UK Science Platform](https://rsp.lsst.ac.uk/) and [Rubin Science Platform](https://data.lsst.cloud). These resources may be better suited for long-term archival research.
