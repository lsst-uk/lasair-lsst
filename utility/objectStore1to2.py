import os, sys, time
sys.path.append('../common/src')
import objectStore

# How to do multiprocessing
# python3 objectStore1to2.py 4 0 &
# python3 objectStore1to2.py 4 1 &
# python3 objectStore1to2.py 4 2 &
# python3 objectStore1to2.py 4 3; date

step  = 1
start = 0
if len(sys.argv) >=3:
    step = int(sys.argv[1])
    start = int(sys.argv[2])
print('Step %d start %d' % (step, start))

dir1 = '/mnt/cephfs/lasair/fits'
dir2 = '/mnt/cephfs/lasair/fits2'
#store1 = objectStore.objectStore(suffix='fits', fileroot=dir1, double=False)
store2 = objectStore.objectStore(suffix='fits', fileroot=dir2, double=True)

# typical filename = '2267526684315015040_cutoutDifference'
n = 0
nfile = 1
tstart = time.time()
for i in range(start, 4096, step):
    d4 = '%03x' % i
    for filename_fits in os.listdir(dir1 +'/'+ d4):
        filename = filename_fits.split('.')[0]
        n2 = store2.getFileName(filename, mkdir=True)
        cmd = 'cp -p %s/%s/%s.fits %s' % (dir1, d4, filename, n2)
        os.system(cmd)
        nfile += 1
    t = (time.time() - tstart)/nfile
    print('Done %s -- %d files at %.0f ms each' % (d4, nfile, 1000*t))
