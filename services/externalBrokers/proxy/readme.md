### Proxy Annotators

A "proxy annotator" is a Lasair annotator that is managed by the Lasair team rather than by a user, pulling data by Kafka from a remote endpoint, and converting to a Lasair annotation. Examples so far are Alerce, AMPEL, and Fink annotations, where each may involve multiple annotators ("modules") with different science goals.

Instead of the current encrusted evolved code, there should be three layers:
- The proxy orchestrator that is run regularly, can write to the terminal or logfile, and is responsible for calling and receiving returned annotations, then ingesting them into Lasair.
- The provider layer that opens connections with a secret login and polls for messages, then calls:
- The annotation layer that converts a message to the Lasair annotation semantics of `classification` and `classdict`. Each provider may have multiple annotators. 

A "module" is the provider's name for the annotator. For example the Fink annotator that Lasair calls "fink_snn" is known to the Fink server as "fink_extragalactic_lt20mag_candidate_lsst". 
Each annotator will be owned by an entity that may not be human (eg "Fink") but has an associated `API_TOKEN`. In the `settings.py` that supports these annotators, some keywords are provider-dependent or module-dependent, but others have specific meaning, for example 
- `CODE`: the name of the python file to be executed for a given annotator
- `ANNOTATOR`: the topic name of the associated Lasair annotator
- `API_TOKEN`: the token to be used for ingesting annotations to Lasair
- `SERVERS`: Kafka endpoint to connect to
- `MODULE`: provider's name for the annotator.

This code is meant to be run as a cron, listing the appropriate proxy annotators to be run, for example:
```
python3 proxy_annotators.py \
    --verbose --maxtry=5 \
    --group_id=test123 \
    --ann=fink_snn \
    --ann=alerce_stamp \
    --ann=alerce_lc \
    --ann=ampel_infant \
    --ann=ampel_extragal \
```
