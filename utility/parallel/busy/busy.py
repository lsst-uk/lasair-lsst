""" busy.py
Time waster, number of seconds ~= program argument
"""
import sys, random, math, time
tstart = time.time()
N = 5000000 * int(sys.argv[1])
for i in range(N):
    x = math.sqrt(random.random())
print('%.0f: Finished' % (time.time()-tstart))
