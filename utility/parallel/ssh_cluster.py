""" Make a cluster from nodes, where you can ssh to any node from the head node with no auth.
The input is a set of hosts and a set of commands to be executed on them.
Uses the parallel-SSH library https://pypi.org/project/parallel-ssh/
To see how it works, try the "busy" example
WARNING: there is a ~60 second lag between the remote program finishing and this code finding out.
"""
import sys, time, random
from pssh.clients import ParallelSSHClient

def run_commands_on_hosts(cmdlist, hosts):
    clients = [ParallelSSHClient([host]) for host in hosts]
    
    outputs = [None for host in hosts]
    tstart = time.time()
    while 1:
        nfinished = 0
        for i in range(len(clients)):
            if clients[i]:
                # if a job is finished
                if clients[i].finished():
                    # print the outputs
                    if outputs[i]:
                        for host_output in outputs[i]:
                            print("%d: Host %d: exit code %s" % (
                              time.time()-tstart, i, host_output.exit_code))
                            for line in list(host_output.stdout):
                                print('    ' + line)
    
                    # start another if there is a job
                    if len(cmdlist) > 0:
                        cmd = cmdlist.pop()
                        print('%d: Starting %s on host %d' % (
                            time.time()-tstart, cmd, i))
                        outputs[i] = clients[i].run_command(cmd)
                    else:
                        clients[i] = None
            else:
                nfinished += 1
        if nfinished == len(hosts):
            print('All finished in %d seconds' % int(time.time()-tstart))
            break
        else:
            time.sleep(5)
