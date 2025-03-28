# A simple cutout store implemented on Cassandra
# Roy Williams and Ken Smith 2023
# Added trimming and compression - GF 2025

from cassandra.cluster import Cluster
from concurrent.futures import Future
from math import ceil
import lz4.frame
try:
    import settings
except ModuleNotFoundError:
    pass


def trim_fits(data: bytes) -> bytes:
    """Trim FITS data by removing all but the fist extent."""
    bitpix = 0
    naxis1 = 0
    naxis2 = 0
    offset = 0
    remaining_headers = 3
    while True:
        hu = data[offset:offset + 80]  # header unit
        kw = hu[:8].split()[0]  # keyword
        if kw == b'BITPIX':
            bitpix = abs(int(f"{hu[10:80].split()[0].decode()}"))
            remaining_headers -= 1
        elif kw == b'NAXIS1':
            naxis1 = int(f"{hu[10:80].split()[0].decode()}")
            remaining_headers -= 1
        elif kw == b'NAXIS2':
            naxis2 = int(f"{hu[10:80].split()[0].decode()}")
            remaining_headers -= 1
        offset += 80
        if remaining_headers == 0:
            # stop once we've got all the headers we need
            break
        if hu[0:3] == b'END' or offset == 2800:
            # reached end of headers without getting everything
            raise Exception("Error parsing FITS headers")
    data_size = int(naxis1 * naxis2 * bitpix / 8)
    ext = 2880 * (ceil(data_size / 2880) + 1)
    return data[:ext]


class cutoutStore():
    """cutoutStore.
    """

    def __init__(self, pass_session=None):
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
                self.session.default_timeout = 90
            except Exception as e:
                print('Cutoutcass session failed to create: ' + str(e))
                self.session = None
        self.trim = getattr(settings, 'CUTOUT_TRIM', False)
        self.compress = getattr(settings, 'CUTOUT_COMPRESS', False)

    def getCutout(self, cutoutId: str, imjd: int):
        """getCutout.

        Args:
            cutoutId: identifier for blob
            imjd: MJD of the source
        """

        sql = "select cutoutimage from cutouts where imjd=%d and \"cutoutId\"='%s'"
        sql = sql % (imjd, cutoutId)

        rows = self.session.execute(sql)
        for row in rows:
            if self.compress:
                image = lz4.frame.decompress(row.cutoutimage)
            else:
                image = row.cutoutimage
            return image
        return None

    def putCutout(self, cutoutId: str, imjd: int, objectId: str, cutoutBlob: bytes):
        """putCutout. put in the blob with given identifier

        Args:
            cutoutId: identifier for blob
            imjd: MJD of the source
            objectId: identifier of the associated object
            cutoutBlob: binary data
        """
        if self.trim:
            cutoutBlob = trim_fits(cutoutBlob)
        if self.compress:
            cutoutBlob = lz4.frame.compress(cutoutBlob, compression_level=0)

        sql = f'insert into cutouts ("cutoutId",imjd,"objectId",cutoutimage) values (%s,{imjd},{objectId},%s)'
        blobData = bytearray(cutoutBlob)
        self.session.execute(sql, [cutoutId, blobData])

        # then the cutoutId keyed by objectId
        sql = f'insert into cutoutsbyobject ("cutoutId","objectId") values (%s,{objectId})'
        self.session.execute(sql, [cutoutId])

    def putCutoutAsync(self, cutoutId, imjd, objectId, cutoutBlob) -> [Future]:
        """putCutoutAsync. put in the blob with given identifier. 
        Also put data into cutoutsbyobject, but without the blob.
        Use async communication and return a list of future objects.

        Args:
            cutoutId:
            cutoutBlob:
        """
        # first the blob keyed by imjd,cutoutId
        sql = f'insert into cutouts ("cutoutId",imjd,"objectId",cutoutimage) values (%s,{imjd},{objectId},%s)'
        blobData = bytearray(cutoutBlob)
        cutoutReturn = self.session.execute_async(sql, [cutoutId, blobData])

        # then the cutoutId keyed by objectId
        sql = f'insert into cutoutsbyobject ("cutoutId","objectId") values (%s,{objectId})'
        cutoutsByObjectReturn = self.session.execute_async(sql, [cutoutId])

        return [cutoutReturn, cutoutsByObjectReturn]

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
