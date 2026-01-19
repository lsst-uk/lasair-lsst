import json
import sys
import math
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


class lightcurve_fetcher_error(Exception):
    def __init__(self, message):
        self.message = message


class lightcurve_fetcher():
    def __init__(self, cassandra_hosts, reliabilityThreshold=0):
        self.using_cassandra = True
        self.cluster = Cluster(cassandra_hosts)
        self.session = self.cluster.connect()
        # Set the row_factory to dict_factory, otherwise
        # the data returned will be in the form of object properties.
        self.session.row_factory = dict_factory
        self.session.set_keyspace('lasair')
        self.reliabilityThreshold = reliabilityThreshold

    def fetch(self, diaObjectId, lite=True):
        # fetch the diaSources from Cassandra
        if lite:
            query = 'SELECT "diaSourceId", "midpointMjdTai", band, "psfFlux", "psfFluxErr", reliability '
        else:
            query = 'SELECT * '
        query += 'FROM diaSources WHERE "diaObjectId" = %s' % diaObjectId

        ret = self.session.execute(query)
        diaSources = []
        for diaSource in ret:
            if not math.isnan(diaSource['psfFlux'] and \
                    diaSource['reliability'] > self.reliabilityThreshold):
                diaSources.append(diaSource)

        # fetch the diaForcedSources from Cassandra
        if lite:
            query = 'SELECT "midpointMjdTai", "band", "psfFlux", "psfFluxErr" '
        else:
            query = 'SELECT * '
        query += 'from diaForcedSources where "diaObjectId" = %s' % diaObjectId

        ret = self.session.execute(query)
        diaForcedSources = []
        for diaForcedSource in ret:
            if not math.isnan(diaForcedSource['psfFlux']):
                diaForcedSources.append(diaForcedSource)

        # fetch the diaObject from Cassandra
        # Note: return is two obj if lite else three obj
        if lite:
            return (diaSources, diaForcedSources)
        else:
            query = 'SELECT * from diaObjects where "diaObjectId" = %s' % diaObjectId
            ret = self.session.execute(query)
            diaObject = ret[0]
            return (diaObject, diaSources, diaForcedSources)

    def close(self):
        if self.session:
            self.cluster.shutdown()


if __name__ == "__main__":
    LF = lightcurve_fetcher(cassandra_hosts=['192.168.0.11'])

    (diaSources, diaForcedSources) = LF.fetch(177261894535479587)
    print(len(diaSources))
    print(len(diaForcedSources))
