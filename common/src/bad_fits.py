import os
from astropy.io import fits

def bad_moc_stream(stream):
    try:
        hdu = fits.open(stream)
        header = dict(hdu[1].header)
    except Exception as e:
        return 'Cannot open as a FITS file %s' % str(e)
    if 'MOCORDER' in header and int(header['MOCORDER']) > 14:
        return 'Bad MOCORDER in MOC file'
    return None

def bad_moc_file(filename):
    stream = open(filename, 'rb')
    message = bad_moc_stream(stream)
    stream.close()
    return message

if __name__ == '__main__':
    dir = '/mnt/cephfs/lasair/areas'
    for filename in os.listdir(dir):
        filename = dir +'/'+ filename
        print(filename, bad_moc_file(filename))
