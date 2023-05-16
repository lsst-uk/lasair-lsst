import json
import sys
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


class lightcurve_fetcher_error(Exception):
    def __init__(self, message):
        self.message = message


class lightcurve_fetcher():
    def __init__(self, cassandra_hosts=None, fileroot=None):
        if cassandra_hosts is not None:
            self.using_cassandra = True
            self.cluster = Cluster(cassandra_hosts)
            self.session = self.cluster.connect()
            # Set the row_factory to dict_factory, otherwise
            # the data returned will be in the form of object properties.
            self.session.row_factory = dict_factory
            self.session.set_keyspace('lasair')
        elif fileroot is not None:
            self.using_cassandra = False
            self.fileroot = fileroot
            self.session = None
        else:
            raise lightcurve_fetcher_error('Must give either cassandra_hosts or fileroot')

    def fetch(self, diaObjectId, full=False):
        if full:
            query = "SELECT * "
        else:
            query = "SELECT diaSourceId, midPointTai, ra, decl, filterName, nid, psFlux, psFluxErr "
        query += "from diaSources where diaObjectId = %s" % diaObjectId
        ret = self.session.execute(query)
        diaSources = []
        for diaSource in ret:
            diaSources.append(diaSource)

        query = "SELECT midPointTai, filterName, psFlux "
        query += "from diaForcedSources where diaObjectId = %s" % diaObjectId
        ret = self.session.execute(query)
        diaForcedSources = []
        for diaForcedSource in ret:
            diaForcedSources.append(diaForcedSource)

        query = "SELECT midPointTai, filterName, diaNoise "
        query += "from diaNondetectionLimits where diaObjectId = %s" % diaObjectId
        ret = self.session.execute(query)
        diaNondetectionLimits = []
        for diaNondetectionLimit in ret:
            diaNondetectionLimits.append(diaNondetectionLimit)

        return (diaSources, diaForcedSources, diaNondetectionLimits)

    def close(self):
        if self.session:
            self.cluster.shutdown()


if __name__ == "__main__":
    LF = lightcurve_fetcher(cassandra_hosts=['192.168.0.11'])

    (diaSources, diaForcedSources, diaNondetectionLimits) = LF.fetch(177261894535479587)
    print(len(diaSources))
    print(len(diaForcedSources))
    print(len(diaNondetectionLimits))
