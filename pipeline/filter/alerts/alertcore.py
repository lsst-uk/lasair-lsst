import sys
import datetime
import numbers
import math
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

from filtercore import Filter
from transfer import fetch_attrs
from alerts.features.FeatureGroup import FeatureGroup

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid
import db_connect
import manage_status


sys.path.append('alerts')
import sherlock
import filters
import watchlists
import watchmaps
import mmagw

def now():
    return datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")

class AlertFilter(Filter):
    ### AlertFilter is subclass of Filter
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sfd = None
        self.csv_attrs = {}

    ### set up an AlertFilter, after setting up the Filter
    def setup(self):
        # get the Filter object set up 
        super().setup()

        # get the order of the attributes for all tables transferred by CSV
        table_list = [
            'objects',
            'sherlock_classifications',
            'watchlist_hits',
            'area_hits',
            'mma_area_hits',
        ]
        try:
            main_database = db_connect.remote(allow_infile=True)
            for table_name in table_list:
                self.csv_attrs[table_name] = fetch_attrs(main_database, table_name, log=self.log)
        except Exception as e:
            self.log.error('ERROR connecting to main database: %s' % str(e))

        # set up the extinction factory
        if not self.sfd:
            try:
                self.sfd = SFDQuery()
            except Exception as e:
                self.log.error('ERROR in Filter: cannot set up SFDQuery extinction' + str(e))


    # this method will be called from above when a batch of messages is ready
    def setup_batch(self):
        # truncate local databases
        self.execute_local_query('TRUNCATE TABLE objects')
        self.execute_local_query('TRUNCATE TABLE sherlock_classifications')
        self.execute_local_query('TRUNCATE TABLE watchlist_hits')
        self.execute_local_query('TRUNCATE TABLE area_hits')

        # set up the timers
        self.timers = {}
        for name in ['ffeatures', 'fwatchlist', 'fwatchmap', \
                'fmmagw', 'ffilters', 'ftransfer', 'ftotal']:
            self.timers[name] = manage_status.timer(name)

        self.timers['ftotal'].on()
        self.log.info('FILTER batch start %s' % now())
        self.log.info("Topic is %s" % self.topic_in)


    def run_batch(self, n_messages):
        """Top level method that processes an alert batch.

        Does the following:
         - Consume alerts from Kafka
         - Run watchlists
         - Run watchmaps
         - Run user filters
         - Run annotation queries
         - Build CSV file
         - Transfer to main database"""

        self.setup()

        # consume the alerts from Kafka
        # ask the superclass to get these
#        self.timers['ffeatures'].on()
#        nalerts = self.consume_messages()
#        self.timers['ffeatures'].off()

        # run the watchlists
        self.log.info('WATCHLIST start %s' % now())
        self.timers['fwatchlist'].on()
        nhits = watchlists.watchlists(self)
        self.timers['fwatchlist'].off()
        if nhits is not None:
            self.log.info('WATCHLISTS got %d' % nhits)
        else:
            self.log.error("ERROR in filter/watchlists")

        # run the watchmaps
        self.log.info('WATCHMAP start %s' % now())
        self.timers['fwatchmap'].on()
        nhits = watchmaps.watchmaps(self)
        self.timers['fwatchmap'].off()
        if nhits is not None:
            self.log.info('WATCHMAPS got %d' % nhits)
        else:
            self.log.error("ERROR in filter/watchmaps")

        # run the MMA/GW events
        self.log.info('MMA/GW start %s' % now())
        self.timers['fmmagw'].on()
        nhits = mmagw.mmagw(self)
        self.timers['fmmagw'].off()
        if nhits is not None:
            self.log.info('MMA/GW got %d' % nhits)
        else:
            self.log.error("ERROR in filter/mmagw")

        # run the user filters
        self.log.info('Filters start %s' % now())
        self.timers['ffilters'].on()
        ntotal = filters.filters(self)
        self.timers['ffilters'].off()
        if ntotal is not None:
            self.log.info('FILTERS got %d' % ntotal)
        else:
            self.log.error("ERROR in filter/filters")

        # build CSV file with local database and transfer to main
        if self.transfer:
            self.timers['ftransfer'].on()
            commit = self.transfer_to_main()
            self.timers['ftransfer'].off()
            self.log.info('Batch ended')
            if not commit:
                self.log.info('Transfer to main failed, no commit')
                return 0

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
        self.log.info('%d alerts processed\n' % n_messages)
        return n_messages

    def handle_message_list(self, alertList):
        """alert_filter: handle a list of alerts
        """
        raList   = []
        declList = []
        for alert in alertList:
            raList  .append(alert['diaObject']['ra'])
            declList.append(alert['diaObject']['decl'])
        c = SkyCoord(raList, declList, unit="deg", frame='icrs')
        ebvList = self.sfd(c)
        nalert = 0
        for ebv, alert in zip(ebvList, alertList):
            alert['ebv'] = ebv
            nalert += self.handle_alert(alert)
        if self.verbose:
            print('handle_alert_list: %d in %d out' % (len(alertList), nalert))
        return nalert

    def handle_alert(self, alert):
        # Filter to apply to each alert.
        diaObjectId = alert['diaObject']['diaObjectId']

        # really not interested in alerts that have no detections!
        if len(alert['diaSourcesList']) == 0:
            if self.verbose:
                print('No diaSources')
            return 0

        # build the insert query for this object.
        # if not wanted, returns 0
        query = self.create_insert_query(alert)
        if not query:
            if self.verbose:
                print('Failed to make insert query')
                print(json.dumps(alert, indent=2))
            return 0
        self.execute_local_query(query)

        # now ingest the sherlock_classifications
        if 'annotations' in alert:
            annotations = alert['annotations']
            if 'sherlock' in annotations:
                for ann in annotations['sherlock']:
                    if "transient_object_id" in ann:
                        ann.pop('transient_object_id')
                    ann['diaObjectId'] = diaObjectId
                    query = self.create_insert_sherlock(ann)
                    self.execute_local_query(query)
        return 1

    @staticmethod
    def create_insert_query(alert: dict):
        """create_insert_query.
        Creates an insert sql statement for building the object and
        a query for inserting it.

        Args:
            alert:
        """

        lasair_features = FeatureGroup.run_all(alert)
        if not lasair_features:
            if self.verbose:
                print('Features did not run')
                print(json.dumps(alert, indent=2))
            return None

        # Make the query
        query_list = []
        query = 'REPLACE INTO objects SET '
        for key, value in lasair_features.items():
            if value is None:
                query_list.append(key + '=NULL')
            elif isinstance(value, numbers.Number) and (math.isnan(value) or math.isinf(value)):
                query_list.append(key + '=NULL')
            elif isinstance(value, str):
                query_list.append(key + '="' + str(value) + '"')
            else:
                query_list.append(key + '=' + str(value))
        query += ',\n'.join(query_list)
        return query

    @staticmethod
    def create_insert_sherlock(ann: dict):
        """create_insert_sherlock.
        Makes the insert query for the sherlock classification
    
        Args:
            ann:
        """
        # all the sherlock attrs that we want for the database
        attrs = [
            "classification",
            "diaObjectId",
            "association_type",
            "catalogue_table_name",
            "catalogue_object_id",
            "catalogue_object_type",
            "raDeg",
            "decDeg",
            "separationArcsec",
            "northSeparationArcsec",
            "eastSeparationArcsec",
            "physical_separation_kpc",
            "direct_distance",
            "distance",
            "best_distance",
            "best_distance_flag",
            "best_distance_source",
            "z",
            "photoZ",
            "photoZErr",
            "Mag",
            "MagFilter",
            "MagErr",
            "classificationReliability",
            "major_axis_arcsec",
            "annotator",
            "additional_output",
            "description",
            "summary",
        ]
        sets = {}
        for key in attrs:
            sets[key] = None
        for key, value in ann.items():
            if key in attrs and value:
                sets[key] = value
    
        # this hack adds back in the deprecated 'distance' as 'best_distance'
        if 'best_distance' in ann:
            sets['distance'] = ann['best_distance']
    
        if 'description' in attrs and 'description' not in ann:
            sets['description'] = 'no description'
        # Build the query
        query_list = []
        query = 'REPLACE INTO sherlock_classifications SET '
        for key, value in sets.items():
            if value is None:
                query_list.append(key + '=NULL')
            else:
                query_list.append(key + '=' + "'" + str(value).replace("'", '') + "'")
        query += ',\n'.join(query_list)
        return query

