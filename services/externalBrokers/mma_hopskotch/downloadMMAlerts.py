"""
Download GW and Icecube Alerts and convert to MOC files.
https://emfollow.docs.ligo.org/userguide/tutorial/multiorder_skymaps.html

This code written by Ken Smith and Roy Williams 2026

Usage:
  %s [--type=<alertType>] [--directory=<directory>] [--contours=<contours>] [--logfile=<logfile>] [--superevents] [--earliest]
  %s (-h | --help)

Options:
  -h --help                         Show this screen.
  --type=<alertType>                Can be GW or Icecube [default: GW]
  --directory=<directory>           Directory to where the maps and MOCs will be written [default: /tmp].
  --contours=<contours>             MOC contoursm separated by commas,  no spaces [default: 90]
  --logfile=<logfile>               log file [default: stdout]
  --superevents                     Only deal with superevents. 
  --earliest                        Start from the earliest message in the queue. (Default is the latest.)
"""
import sys
from docopt import docopt
import logging
from hopskotch_utils import hop_reader
import readGW, readIcecube

# in settings we expect SCIMMA_AUTH_USERNAME, SCIMMA_AUTH_PASSWORD, HOPSKOTCH_GROUP_ID
sys.path.append('../../../common')
import settings

def listen(options):
    """listen.
            
    Args:   
        options:
    """ 

    # set up the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if options['--logfile'] == 'stdout':
        fh = logging.StreamHandler(sys.stdout)
    else:
        fh = logging.FileHandler(options['--logfile'])
    formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formatstr)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # which alerts are we fetching?
    if options['--type'] == 'GW':
         topic = 'igwn.gwalert'
    elif options['--type'] == 'Icecube':
        topic = 'gcn.classic.text.ICECUBE_CASCADE'
    else:
        logger.error(f'Unknown event type {options['--type']}. Exiting')
        sys.exit()

    # set up hopskotch
    scimma_auth_username = settings.SCIMMA_AUTH_USERNAME
    scimma_auth_password = settings.SCIMMA_AUTH_PASSWORD
    group_id             = settings.HOPSKOTCH_GROUP_ID
    hr = hop_reader(scimma_auth_username, scimma_auth_password, \
        topic, group_id, earliest=options['--earliest'])

    # Hopskotch has no timeout. So this just waits forever.
    while True:
        print('polling')
        dataDict = hr.poll()
        print('got event')

        process according to event type
        if options['--type'] == 'GW':
            readGW.handleDataDict(dataDict, options, logger)
        elif options['--type'] == 'Icecube':
            readIcecube.handleDataDict(dataDict, options, logger)
        else:
            logger.error(f'Unknown event type {options['--type']}. Exiting')
            continue

if __name__ == '__main__':
    options = docopt(__doc__, version='0.0.10')
    listen(options)
