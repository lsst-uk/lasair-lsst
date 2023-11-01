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

    def __init__(self, pass_session = None):
        """__init__.

        """
        if pass_session:
            # will use existing session and keyspace
            self.session = pass_session

        else:
            # create session and use keyspace 'cutouts'
            try:
                hosts = settings.CUTOUTCASS_HOSTS
            except:
                hosts = ['localhost']
            self.cluster = Cluster(hosts)
            self.session = self.cluster.connect()
            self.session.set_keyspace('cutouts')
    
    def getObject(self, objectId, imjd=None):
        """getObject.

        Args:
            objectId: identifier for blob
        """
        sql = "select cutoutimage from cutouts where cutout='%s'"
        sql = sql % objectId
        rows = self.session.execute(sql)
        for row in rows:
            return row.cutoutimage

    def putObject(self, objectId, mjd, objectBlob):
        """putObject. put in the blob with given identifier

        Args:
            objectId:
            objectBlob:
        """
        sql = f"insert into cutouts (cutout,mjd,cutoutimage) values (%s,{mjd},%s)"
        blobData = bytearray(objectBlob)
        self.session.execute(sql, [objectId, blobData])

    def close(self):
        self.cluster.shutdown()

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    import settings
    objectId = '181071530527032078_cutoutTemplate'
    fp = open(objectId + '.fits', 'rb')
    objectBlob = fp.read(cutout)
    fp.close()

    mjd = 60000
    osc = objectStoreCass()
    osc.putObject(objectId, mjd, objectBlob)

    cutout = osc.getObject(objectId)
    fp = open(objectId + '_copy.fits', 'wb')
    fp.write(cutout)
    fp.close()
