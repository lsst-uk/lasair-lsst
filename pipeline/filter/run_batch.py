import os, sys, time
from datetime import datetime
import start_batch, end_batch
import consume_alerts, watchlists, watchmaps, filters
import signal

sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import date_nid, db_connect, manage_status, lasairLogging
from docopt import docopt

def now():
    return datetime.utcnow().strftime("%H:%M:%S")

def sigterm_handler(signum, frame):
    pass

signal.signal(signal.SIGTERM, sigterm_handler)

def run_batch():
    batch = start_batch.Batch()

    print('clear local caches')
    batch.truncate_local_database()

    batch.timers['ftotal'].on()
    
    batch.log.info('FILTER start %s' % now())
    batch.log.info("Topic is %s" % batch.topic_in)

    ##### consume the alerts from Kafka
    batch.make_kafka_consumer()
    batch.timers['ffeatures'].on()
    nalerts = consume_alerts.consume_alerts(batch)
    batch.timers['ffeatures'].off()
    
    if nalerts > 0:
        ##### run the watchlists
        log.info('WATCHLIST start %s' % now())
        batch.timers['fwatchlist'].on()
        nhits = watchlists.watchlists(batch)
        batch.timers['fwatchlist'].off()
        if nhits is not None:
            batch.log.info('WATCHLISTS got %d' % nhits)
        else:
            batch.log.error("ERROR in filter/watchlists")
    
        ##### run the watchmaps
        log.info('WATCHMAP start %s' % now())
        batch.timers['fwatchmap'].on()
        nhits = watchmaps.watchmaps(batch)
        batch.timers['fwatchmap'].off()
        if nhits is not None:
            batch.log.info('WATCHMAPS got %d' % nhits)
        else:
            batch.log.error("ERROR in filter/watchmaps")
    
        ##### run the user filters
        batch.log.info('Filters start %s' % now())
        batch.timers['ffilters'].on()
        ntotal = filters.filters(batch)
        batch.timers['ffilters'].off()
        if ntotal is not None:
            batch.log.info('FILTERS got %d' % ntotal)
        else:
            batch.log.error("ERROR in filter/filters")
    
        ##### run the annotation queries
        batch.log.info('ANNOTATION FILTERS start %s' % now())
        ntotal = filters.fast_anotation_filters(batch)
        if ntotal is not None:
            batch.log.info('ANNOTATION FILTERS got %d' % ntotal)
        else:
            batch.log.error("ERROR in filter/fast_annotation_filters")
    
        ##### build CSV file with local database
        batch.timers['ftransfer'].on()
        commit = end_batch.transfer_to_main(batch)
        batch.timers['ftransfer'].off()
        log.info('Batch ended')

        if not commit:
            log.info('Transfer to main failed, no commit')
            time.sleep(600)
            return 0

    batch.timers['ftotal'].off()
    end_batch.write_stats(batch, nalerts)
    batch.log.info('%d alerts processed' % nalerts)
    return nalerts

if __name__ == '__main__':
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("filter")
    nalerts = run_batch()
    sys.exit(nalerts)
