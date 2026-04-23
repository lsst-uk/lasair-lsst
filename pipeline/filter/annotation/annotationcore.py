import sys
import datetime
import numbers
import math
import json

from annotation import filters
from filtercore import Filter
from transfer import fetch_attrs

sys.path.append('../../common')
import settings

sys.path.append('../../webserver/lasair')
sys.path.append('../../../../webserver/lasair')
from lightcurves import lightcurve_fetcher

def now():
    return datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")

class AnnotationFilter(Filter):
    ### AnnotationFilter is subclass of Filter
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ### set up an AnnotationFilter, after setting up the Filter
    def setup(self):
        # get the Filter object set up 
        super().setup()

        # set up cassandra lightcurve fetcher
        try:
            self.lightcurve = lightcurve_fetcher(\
                    cassandra_hosts=settings.CASSANDRA_HEAD,
                    reliabilityThreshold=0.5)
        except Exception as e:
            self.log.error('ERROR in Filter: cannot connect to cassandra' + str(e))


    # this method will be called from above when a batch of messages is ready
    def setup_batch(self):
        # this is the cache of all the annotated diaObjectIds
        # it is used to modify the filters when they run
        self.ann_diaObjectId = {}
        return

    def ingest_message_list(self, annotationList):
        """insert_message_list: handle a list of annotations of the form
        [ann1, ann2, ....]
        """
        nannotation = 0
        for ann in annotationList:
            nannotation += self.ingest_annotation(ann)
        if self.verbose:
            print('ingest_annotation_list: %d in %d out' % (len(annotationList), nannotation))
        return nannotation

    def ingest_annotation(self, annotation):
        # keep list of all objectId in this batch
        if 'topic' in annotation:
            annotator = annotation['topic']
        else:
            return 0

        # self.ann_diaObjectId = {
        #     'topic1':[oid1, oid2, ...], 
        #     'topic2':[...] }
        if annotator in self.ann_diaObjectId:
            self.ann_diaObjectId[annotator].append(annotation['diaObjectId'])
        else:
            self.ann_diaObjectId[annotator] = [annotation['diaObjectId']]

        # put the annotation in the database
        query = 'REPLACE INTO annotations ('
        query += 'diaObjectId, topic, version, classification, explanation, classdict, url'
        query += ') VALUES ('
        query += "'%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        query = query % (
                annotation['diaObjectId'], 
                annotation['topic'], 
                annotation['version'], 
                annotation['classification'], 
                annotation['explanation'], 
                annotation['classdict'], 
                annotation['url'])

        self.execute_remote_query(query)
        return 1

    def post_ingest(self, n_messages):
        """Top level method that processes an alert batch.

        Does the following:
         - Consume alerts from Kafka
         - Run annotation queries
        """
        if self.verbose:
            print('List of annotations:', self.ann_diaObjectId)

        # run the annotation queries
        self.log.info('ANNOTATION FILTERS start %s' % now())
        ntotal = filters.annotation_filters(self)
        if ntotal is not None:
            self.log.info('ANNOTATION FILTERS got %d' % ntotal)
        else:
            self.log.error("ERROR in filter/fast_annotation_filters")

        # commit the kafka
        self.consumer.commit()
