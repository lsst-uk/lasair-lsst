from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord
import sherlock
import filters
import watchlists
import watchmaps
import mmagw

class AlertFilter(Filter):
    def __init__(self, *args):
        super().__init__(*args)

    def run_batch(self):
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

        # set up the timers
        timers = {}
        for name in ['ffeatures', 'fwatchlist', 'fwatchmap', \
                'fmmagw', 'ffilters', 'ftransfer', 'ftotal']:
            timers[name] = manage_status.timer(name)

        self.truncate_local_database()

        timers['ftotal'].on()
        self.log.info('FILTER batch start %s' % now())
        self.log.info("Topic is %s" % self.topic_in)

        # consume the alerts from Kafka
        timers['ffeatures'].on()
        nalerts = self.consume_alerts()
        timers['ffeatures'].off()

        if nalerts > 0:
            # run the watchlists
            self.log.info('WATCHLIST start %s' % now())
            timers['fwatchlist'].on()
            nhits = watchlists.watchlists(self)
            timers['fwatchlist'].off()
            if nhits is not None:
                self.log.info('WATCHLISTS got %d' % nhits)
            else:
                self.log.error("ERROR in filter/watchlists")

            # run the watchmaps
            self.log.info('WATCHMAP start %s' % now())
            timers['fwatchmap'].on()
            nhits = watchmaps.watchmaps(self)
            timers['fwatchmap'].off()
            if nhits is not None:
                self.log.info('WATCHMAPS got %d' % nhits)
            else:
                self.log.error("ERROR in filter/watchmaps")

            # run the MMA/GW events
            self.log.info('MMA/GW start %s' % now())
            timers['fmmagw'].on()
            nhits = mmagw.mmagw(self)
            timers['fmmagw'].off()
            if nhits is not None:
                self.log.info('MMA/GW got %d' % nhits)
            else:
                self.log.error("ERROR in filter/mmagw")

            # run the user filters
            self.log.info('Filters start %s' % now())
            timers['ffilters'].on()
            ntotal = filters.filters(self)
            timers['ffilters'].off()
            if ntotal is not None:
                self.log.info('FILTERS got %d' % ntotal)
            else:
                self.log.error("ERROR in filter/filters")

            # build CSV file with local database and transfer to main
            if self.transfer:
                timers['ftransfer'].on()
                commit = self.transfer_to_main()
                timers['ftransfer'].off()
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

        # Clean up
        self.alert_dict.clear()

        # Write stats for the batch
        timers['ftotal'].off()
        self.write_stats(timers, nalerts)
        self.log.info('%d alerts processed\n' % nalerts)
        return nalerts

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


    def handle_alert_list(self, alertList):
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
        query = Filter.create_insert_query(alert)
        if not query:
            if self.verbose:
                print('Failed to make insert query')
                print(json.dumps(alert, indent=2))
            return 0
        self.execute_query(query)

        # now ingest the sherlock_classifications
        if 'annotations' in alert:
            annotations = alert['annotations']
            if 'sherlock' in annotations:
                for ann in annotations['sherlock']:
                    if "transient_object_id" in ann:
                        ann.pop('transient_object_id')
                    ann['diaObjectId'] = diaObjectId
                    query = Filter.create_insert_sherlock(ann)
                    self.execute_query(query)
        return 1

