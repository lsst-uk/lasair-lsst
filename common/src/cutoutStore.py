# A simple cutout store implemented on Cassandra
# Roy Williams and Ken Smith 2023

from cassandra.cluster import Cluster
try:
    import settings
except:
    pass
import os

class cutoutStore():
    """cutoutStore.
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
            try:
                self.cluster = Cluster(hosts)
                self.session = self.cluster.connect()
                self.session.set_keyspace('cutouts')
            except Exception as e:
                print('Cutoutcass session failed to create: ' + str(e))
                self.session = None
    
    def getCutout(self, cutoutId, imjd):
        """getCutout.

        Args:
            cutoutId: identifier for blob
        """
        sql = "select cutoutimage from cutouts where imjd=%d and cutoutId='%s'"
        sql = sql % (imjd, cutoutId)
        rows = self.session.execute(sql)
        for row in rows:
            return row.cutoutimage
        return None

    def putCutout(self, cutoutId, imjd, objectId, cutoutBlob):
        """putCutout. put in the blob with given identifier

        Args:
            cutoutId:
            cutoutBlob:
        """
        sql = f"insert into cutouts (cutoutId,imjd,objectId,cutoutimage) values (%s,{imjd},{objectId},%s)"
        blobData = bytearray(cutoutBlob)
        self.session.execute(sql, [cutoutId, blobData])

    def putCutoutAsync(self, cutoutId, imjd, objectId, cutoutBlob):
        """putCutoutAsync. put in the blob with given identifier. Use async communication and return a future object.

        Args:
            cutoutId:
            cutoutBlob:
        """
        sql = f"insert into cutouts (cutoutId,imjd,objectId,cutoutimage) values (%s,{imjd},{objectId},%s)"
        blobData = bytearray(cutoutBlob)
        return self.session.execute_async(sql, [cutoutId, blobData])

    def close(self):
        self.cluster.shutdown()

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    import settings
    imjd = 57072
    cutoutId = '176805391051522611_cutoutTemplate'
    imjd = 60487
    cutoutId = '3068394670028488705_cutoutDifference'

#    fp = open(cutoutId + '.fits', 'rb')
#    cutoutBlob = fp.read(cutout)
#    fp.close()

    osc = cutoutStore()
#    osc.putCutout(cutoutId, cutoutBlob, imjd)

    cutout = osc.getCutout(cutoutId, imjd)
    if cutout:
        fp = open(cutoutId + '_copy.fits', 'wb')
        fp.write(cutout)
        fp.close()
        print('cutout written to file')
    else:
        print('cutout not found')
