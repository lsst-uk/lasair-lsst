# Lasair "parallel" 
* This system is used for rebuilding object features from light curves.
* It can also be used for other data mining of all the light curves.

The system executes multiple tasks on multiple workers, controlled by a head node that can connect to each worker through SSH. It is built with the  "parallel-SSH" library at https://pypi.org/project/parallel-ssh/

Each task is defined by a command line, and each worker by an IP-address, with the assumption that the SSH doesn't require a password. When a worker has finished a task, it is given another, until there are no more tasks left.

Note that there is a approx 60 second delay after the task is finished, before the head node's "finished" function reports true, and a subsequent task sent to that host. So this system works efficiently with large (multi-minute) tasks.

There are two applications of the system so far:
* "busy" is a prototype: it just runs a busy process on the worker
* "rebuild_objects" computes new features for objects in the Lasair database. The light curve is fetched from Cassandra for each one, and the same code used as in the real-time pipeline. To get the same results, only the latest 30 days of the light curve are used. CSV files are created, which can be ingested into the database using the program "csv_to_database".

This experiment computed features for 128,000 objects, with varying numbers of workers and processes-per-worker. For 4 workers, each with 8 processes (bottome right), each job computes 4,000 objects. Here are the times in seconds, including overheads:
| processes \ workers | 1    |   2  |    4 |
|--------------------|------|------|------|
| 1       |      7828  | 3615 | 2735 |
| 2       |      3939  | 1853 | 1089 |
| 4       |      2067  |  927 |  473 |
| 8       |      1066  |  486 |  358 |

The speedup from the slowest to the fastest is 22.

For the 3,700,000 objects in the Lasair database, recomputing all the features would take about 3 hours. 

The files generated from the rust above were uploaded to the Galera database in 1 to 2 minutes, depending on how many files. This upload time for all the objects in the database would be 30 minutes to an hour.
