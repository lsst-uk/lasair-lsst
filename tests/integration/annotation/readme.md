### Testing annotations and tags
- This test can only run on lasair-lsst-dev because it adds records to the live database.
- Program arguments (below) give annotator name/topic and username of owner
- If the annotator name begins "tags_" the behaviour is slightly different
- First create an annotator of the given name/topic with given owner
- Annotations are made with classification set to apple, and another with pear

#### Direct
- Direct annotation is by the code `ann_direct.py`, where an annotator is made, and annotations inserted directly, then we see the results immediately.
- This is how the webserver will run when users add/delete tags
- Two annotations are made, should happen immediately
- For classic, there can only be one annotation per object, so we just get pear, but for tags we get apple and pear

| test | command |
|------|---------|
| classic+direct | `python3 ann_direct.py royg __annot` |
| tags+direct | `python3 ann_direct.py royg tags_roy` |

#### Kafka
- Kafka-mediated annotation is more complicated, using the code `ann_kafka.py`. 
- The `ann_kafka.py` runs via the `filter-annotation` service, that may take
a few seconds to see and respond to the kafka messages, so we sleep until the annotations have arrived.
- This route also means that the filter should be triggered by the arrival 
of the annotations, so we run the kafka consumer.
- Make sure the service is running: in lasair-lsst/deploy do `./start.sh filter-annotation`
- In addition to the annotator, we create a filter that triggers on annotation, with plain kafka output
- If the program is run in `api` mode, make two annotations added via the webserver and kafka
- If run in `direct_kafka` mode, annotations added directly into the kafka stream without using the webserver
- Two annotations are made via Kafka, and it will take a minute for them to arrive
- For classic, we just get apple, for tags we get apple and pear

| test | command |
|------|---------|
| classic+api | `python3 ann_kafka.py royg __annot 10 api` |
| tags+api | `python3 ann_kafka.py royg tags_royg 10 api` |
| classic+kafka | `python3 ann_kafka.py royg __annot 10 direct_kafka` |
| tags+kafka | `python3 ann_kafka.py royg tags_royg 10 direct_kafka` |
