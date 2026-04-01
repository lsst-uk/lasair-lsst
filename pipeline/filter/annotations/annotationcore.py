import sys
import datetime
import numbers
import math

from filtercore import Filter
from transfer import fetch_attrs

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid
import db_connect
import manage_status

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

        ]

    # this method will be called from above when a batch of messages is ready
    def setup_batch(self):
        self.diaObjectIdList = []
        return

    def post_ingest(self, n_messages):
        """Top level method that processes an alert batch.

        Does the following:
         - Consume alerts from Kafka
         - Run annotation queries
        """

        self.setup()

        # run the annotation queries
        self.log.info('ANNOTATION FILTERS start %s' % now())
        ntotal = filters.fast_anotation_filters(self)
        if ntotal is not None:
            self.log.info('ANNOTATION FILTERS got %d' % ntotal)
        else:
            self.log.error("ERROR in filter/fast_annotation_filters")

        # Write stats for the batch
        self.timers['ftotal'].off()
        self.write_stats(self.timers, n_messages)
        self.log.info('%d annotationss processed\n' % n_messages)
        return n_messages

    def ingest_message_list(self, annotationsList):
        """insert_message_list: handle a list of annotations
        """
        nannotation = 0
        for annotation in annotationList:
            nannotation += self.ingest_annotation(annotation)
        if self.verbose:
            print('ingest_annotation_list: %d in %d out' % (len(annotationList), nannotation))
        return nannotation

    def ingest_annotation(self, annotation):
        # keep list of all objectId in this batch
        self.diaObjectIdList.append(annotation['diaObjectId'])

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

        try:
            cursor = self.database_remote.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            self.database_remote.commit()
            return 1
        except Exception as e:
            return {'error': "Query failed %d: %s\n" % (e.args[0], e.args[1])}

