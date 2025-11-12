"""
Bulk copy utility. Copy a directory of files in parallel.
Usage:
    bulk_copy.py <src_dir> <dst_dir> [--nprocess=<n>] [--max_size=<bytes>] [--update]

Options:
    --nprocess=<n>     Number of processes [default: 1]
    --max_size=<bytes> Skip files larger than this, default is unlimited
    --update           Update files only if older
"""

import os
from docopt import docopt
from multiprocessing import Pool, current_process
from time import perf_counter


def copy_file(src, dst, update=False):
    print(f"{current_process().name}: {src} -> {dst}")
    size = os.path.getsize(src)
    if update:
        os.system(f"cp --update {src} {dst}")
    else:
        os.system(f"cp {src} {dst}")
    return size


if __name__ == '__main__':
    # deal with arguments
    args = docopt(__doc__)
    nprocess = int(args['--nprocess'])
    max_size = args['--max_size']
    update = args['--update']
    src = args['<src_dir>']
    dst = args['<dst_dir>']

    # make list of files to copy
    files = os.listdir(src)
    copies = []
    for f in files:
        if max_size and os.path.getsize(f"{src}/{f}") > int(max_size):
            continue
        copies.append((f"{src}/{f}", f"{dst}/{f}", update))
    print(f'Copying {len(copies)} files from {src} to {dst} with {nprocess} processes')

    # copy the files
    with Pool(processes=nprocess) as pool:
        t_start = perf_counter()
        sizes = pool.starmap(copy_file, copies)
        t_end = perf_counter()
        print(f"Copied {sum(sizes)}B in {t_end-t_start}s ({sum(sizes)/(t_end-t_start)/1048576}MB/s) ")

