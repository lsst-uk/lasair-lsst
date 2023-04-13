import os, sys
sys.path.append('..')
from ssh_cluster import run_commands_on_hosts

if len(sys.argv) < 3:
    print('Usage: par_runner.py nhost nprocess')
    sys.exit()

print('==============')
os.system('date')
nhost    = int(sys.argv[1])
nprocess = int(sys.argv[2])

global_soff = 1000000 
global_eoff = 1128000
nchunk      = 4
out         = '/mnt/cephfs/roy/features'
hosts       = [
    '192.168.0.40', 
    '192.168.0.27', 
    '192.168.0.8',
    '192.168.0.25',
    ]

hosts = hosts[:nhost]
print(hosts)

cmdlist = []
per_chunk = (global_eoff - global_soff) // nchunk
for ichunk in range(nchunk):
    soff = global_soff + per_chunk*ichunk
    if ichunk == nchunk-1:
        eoff = global_eoff
    else:
        eoff = global_soff + per_chunk*(ichunk+1)
#    print('Chunk %d: %d to %d' % (ichunk, soff, eoff))

    cmd = 'cd /home/ubuntu/lasair4/utility/parallel/rebuild_objects; '
    cmd += 'python3 runner.py --soff=%d --eoff=%d --out=%s --nprocess=%d'
    cmd = cmd % (soff, eoff, out, nprocess)
#    print (cmd)
    cmdlist.append(cmd)

run_commands_on_hosts(cmdlist, hosts)

