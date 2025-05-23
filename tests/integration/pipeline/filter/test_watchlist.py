"""
    Test watchlist infrastucture.

    Tests the integration between the watchlist cache building service and the watchlist pipeline module
    by building a watchlist cache using rebuild_cache and reading it back using read_watchlist_cache_files.
"""
import os, sys
import unittest.main
from unittest import TestCase
import context
sys.path.append('../../../../common/src')
import lasairLogging
sys.path.append('../../../../services')
from services.make_watchlist_files import rebuild_cache
from pipeline.filter.watchlists import check_alerts_against_watchlists
from pipeline.filter.watchlists import read_watchlist_cache_files

cache_dir = 'watchlist_cache/'
chunk_size = 50000
wl_id = 42


class Batch():
    def __init__(self):
        self.log = lasairLogging.getLogger("filter")


def test_cache():
    cone_ids = []
    cone_ralist   = []
    cone_delist   = []
    cone_radius   = []
    cone_names    = []
    alert_ralist = []
    alert_delist = []

    for line in open('../../../unit/pipeline/filter/watchlist_sample.csv').readlines():
        if line[0] == '#': continue
        tok = line.strip().split(',')
        if len(tok) == 5:   # cone
            cone_ids.append(     int(tok[0]))
            cone_ralist.append(float(tok[1]))
            cone_delist.append(float(tok[2]))
            cone_radius.append(float(tok[3])/3600.0)
            cone_names.append(       tok[4])

    cones = {'cone_ids':cone_ids, 'ra':cone_ralist, 'de':cone_delist, 'radius':cone_radius, 'names':cone_names}
    wl_name = 'watchlist_sample'
    max_depth = 13
    rebuild_cache(wl_id, wl_name, cones, max_depth, cache_dir, chunk_size)


def test_alerts():
    alert_ralist = []
    alert_delist = []
    alert_objlist = []

    for line in open('../../../unit/pipeline/filter/watchlist_sample.csv').readlines():
        if line[0] == '#': continue
        tok = line.strip().split(',')
        if len(tok) == 3:   # cone
            alert_ralist.append(float(tok[0]))
            alert_delist.append(float(tok[1]))
            alert_objlist.append(tok[2])
    alertlist = {"obj":alert_objlist, "ra":alert_ralist, "de":alert_delist}

    print('reading cache files')
    batch = Batch()
    watchlistlist = read_watchlist_cache_files(batch, cache_dir)
    print('checking alerts')
    hits = check_alerts_against_watchlists(batch, alertlist, watchlistlist, chunk_size)
    return hits


class FilterWatchlistTest(TestCase):

    @classmethod
    def setUpClass(cls):
        os.system('mkdir ' + cache_dir)

    @classmethod
    def tearDownClass(cls):
        os.system('rm -rf ' + cache_dir)

    def test1_build_cache(self):
        print('test build cache')
        test_cache()
        self.assertTrue(os.path.exists('%s/wl_%d/moc000.fits'   % (cache_dir, wl_id)))
        self.assertTrue(os.path.exists('%s/wl_%d/watchlist.csv' % (cache_dir, wl_id)))

    def test2_alerts(self):
        print('test alerts')
        hits = test_alerts()
        self.assertEqual(len(hits), 49)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()



