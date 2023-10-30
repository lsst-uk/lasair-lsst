# A simple object store implemented on Cassandra
# Roy Williams and Ken Smith 2023

from cassandra.cluster import Cluster
try:
    import settings
except:
    pass
import os

class objectStoreCass():
    """objectStoreCass.
    """

    def __init__(self):
        """__init__.

        """
        try:
            hosts = settings.CUTOUTCASS_HOSTS
        except:
            hosts = ['localhost']
        self.cluster = Cluster(hosts)
        self.session = self.cluster.connect()
        self.session.set_keyspace('cutouts')
    
    def getObject(self, objectId):
        """getObject.

        Args:
            objectId: identifier for blob
        """
        sql = "select cutoutimage from cutouts where cutout='%s'"
        sql = sql % objectId
        rows = self.session.execute(sql)
        for row in rows:
            return row.cutoutimage

    def putObject(self, objectId, objectBlob):
        """putObject. put in the blob with given identifier

        Args:
            objectId:
            objectBlob:
        """
        sql = "insert into cutouts (cutout,cutoutimage) values (%s,%s)"
        blobData = bytearray(objectBlob)
        self.session.execute(sql, [objectId, blobData])

    def close(self):
        self.cluster.shutdown()

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    import settings
    objectId = '181071530527032078_cutoutTemplate'
    osc = objectStoreCass()
    cutout = osc.getObject(objectId)
    fp = open(objectId + '.fits', 'wb')
    fp.write(cutout)
    fp.close()
