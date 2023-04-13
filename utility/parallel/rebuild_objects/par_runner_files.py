import os, sys
sys.path.append('..')
from ssh_cluster import run_commands_on_hosts

def splitgroup(L, n, delim=','):
# from a delimited list L makes a list of delimited strings
# each with n or less from the list
    Llist = L.split(delim)
    gLlist = []
    print('found %d' % len(Llist))
    for i in range(0, len(Llist), n):
        gLlist.append(delim.join(Llist[i:i+n]))
    return gLlist

###################
if len(sys.argv) < 3:
    print('Usage: par_runner.py nprocess indir outdir')
    sys.exit()

print('==============')
os.system('date')
nprocess = int(sys.argv[1])
indir    =     sys.argv[2]
outdir   =     sys.argv[3]

hosts       = [
    'lasair-ztf-filter-0', 
#    'lasair-ztf-filter-1', 
    ]
nhosts = len(hosts)

cmdlist = []
filenames = ','.join(os.listdir(indir))
filegroups = splitgroup(filenames, nprocess)
print('Filegroups are:', filegroups)

for filegroup in filegroups:
    cmd = 'cd /home/ubuntu/lasair4/utility/parallel/rebuild_objects; '
    cmd += 'python3 runner_file.py --in=%s --files=%s --out=%s' % (indir, filegroup, outdir)
    cmdlist.append(cmd)

run_commands_on_hosts(cmdlist, hosts)

