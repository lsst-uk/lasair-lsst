import json
import sys
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


class lightcurve_fetcher_error(Exception):
    def __init__(self, message):
        self.message = message


class lightcurve_fetcher():
    def __init__(self, cassandra_hosts=None):
        if cassandra_hosts is not None:
            self.using_cassandra = True
            self.cluster = Cluster(cassandra_hosts)
            self.session = self.cluster.connect()
            # Set the row_factory to dict_factory, otherwise
            # the data returned will be in the form of object properties.
            self.session.row_factory = dict_factory
            self.session.set_keyspace('adler')
        else:
            print("Must give cassandra hosts eg ['lasair-lsst-cassandra']")

    def fetchObject(self, ssObjectId, full=False):
        obj = {}

        if full:
            query = "SELECT * "
        else:
            query = "SELECT maxextendedness, minextendedness, numobs"
        query += " FROM ssobjects WHERE ssobjectid = %s" % ssObjectId
#        query += " ALLOW FILTERING"
        print('Query is:', query)

        ret = self.session.execute(query)
        for ssObject in ret:
            obj = ssObject

        if full:
            query = "SELECT * "
        else:
            query = "SELECT arcstart, arcend, epoch, incl, e, nobs "
            query += " from mpcorbs where ssObjectId = %s" % ssObjectId
            query += " ALLOW FILTERING"
        ret = self.session.execute(query)
        for mpcorb in ret:
            obj.update(mpcorb)
        return obj

    def fetchSources(self, ssObjectId, full=False):
        sourceDict = {}

        if full:
            query = "SELECT * "
        else:
            query = "SELECT diasourceid, midpointmjdtai, ra, decl, mag"
        query += " FROM diasources WHERE ssobjectid = %s" % ssObjectId
#        query += " ALLOW FILTERING"
        print('Query is:', query)

        ret = self.session.execute(query)
        n = 0
        for diaSource in ret:
            sourceDict[diaSource['diasourceid']] = diaSource
            n += 1

        if full:
            query = "SELECT * "
        else:
            query = "SELECT diasourceid, phaseangle, predictedmagnitude "
            query += " from sssources where ssobjectid = %s" % ssObjectId
            query += " ALLOW FILTERING"
        ret = self.session.execute(query)
        n = 0
        for ssSource in ret:
            n += 1
            sourceDict[ssSource['diasourceid']].update(ssSource)

        # convert dict to a list of values
        sources = []
        for k,v in sourceDict.items():
            sources.append(v)
        return sources

    def close(self):
        if self.session:
            self.cluster.shutdown()


if __name__ == "__main__":
    LF = lightcurve_fetcher(cassandra_hosts=['lasair-lsst-cassandranodes'])

    if len(sys.argv) > 1:
        ssObjectId = sys.argv[1]
    else:
        print('Usage: test_read_cassandra.py ssObjectId')
        sys.exit()

    obj = LF.fetchObject(ssObjectId, full=False)
    print('ssObject+MPCORB is:', json.dumps(obj, indent=2))

    sources = LF.fetchSources(ssObjectId, full=False)
    print('set of ssSource+diaObject:', json.dumps(sources, indent=2))
