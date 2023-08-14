# A simple object store implemented on a file system
# Roy Williams 2020
# updated with primary directory as integer MJD

import os
import hashlib

class objectStore():
    """objectStore.
    """

    def __init__(self, suffix='txt', fileroot='/data'):
        """__init__.

        Args:
            suffix:
            fileroot:
        """
        # make the directories if needed
        os.system('mkdir -p ' + fileroot)
        self.fileroot = fileroot
        self.suffix = suffix
    
    def getFileName(self, objectId, imjd, mkdir=False):
        """getFileName.

        Args:
            objectId:
            imjd:
            mkdir:
        """
        imjddir = self.fileroot +'/' + '%d'%imjd + '/'
        if mkdir:
            try: os.makedirs(imjddir)
            except: pass

        # hash the filename for the directory, use the last 3 digits
        # max number of directories 16**3 = 4096
        h = hashlib.md5(objectId.encode())
        imjddirhash = imjddir + h.hexdigest()[:3] + '/'
        if mkdir:
            try: os.makedirs(imjddirhash)
            except: pass

        return imjddirhash + objectId +'.' + self.suffix

    def getFileObject(self, objectId, imjd):
        """getObject.

        Args:
            objectId:
        """
        f = open(self.getFileName(objectId, imjd), 'rb')
        return f

    def getObject(self, objectId, imjd):
        """getObject.

        Args:
            objectId:
        """
        try:
            f = open(self.getFileName(objectId, imjd))
            str = f.read()
            f.close()
            return str
        except:
            return None

    def putObject(self, objectId, imjd, objectBlob):
        """putObject.

        Args:
            objectId:
            objectBlob:
        """
        filename = self.getFileName(objectId, imjd, mkdir=True)
#        print(objectId, filename)
        if isinstance(objectBlob, str):
            f = open(filename, 'w')
        else:
            f = open(filename, 'wb')
        f.write(objectBlob)
        f.close()

if __name__ == '__main__':
    ost = objectStore('txt', '/home/ubuntu/lasair-lsst/common/src/junk')
    f = ost.getFileName('blabla456', 60000)
    print(f)
    ost.putObject('blabla456', 60000, 'lorem ipsum ...') 
    c = ost.getObject('blabla456', 60000)
    print(c)
