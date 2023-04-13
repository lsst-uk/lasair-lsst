""" Simple usage of the parallel system.
Commands are 16 invocations of the program 'busy', each for about 10 seconds
"""
import sys
sys.path.append('..')
from ssh_cluster import run_commands_on_hosts

if __name__ == "__main__":
    nhosts = int(sys.argv[1])

    hosts      = [
    '192.168.0.40',
    '192.168.0.27',
    '192.168.0.8',
    '192.168.0.25',
    ]
    hosts = hosts[:nhosts]
    print(hosts)
    
    cmdlist = []
    for i in range(16):
        cmd = 'cd /home/ubuntu/lasair4/utility/parallel/busy; '
        cmd += 'python3 busy.py 10'
        cmdlist.append(cmd)
    
    run_commands_on_hosts(cmdlist, hosts)

