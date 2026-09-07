"""Import at the start of tests so that imported packages get resolved properly.
"""

import os
import sys

_here = os.path.dirname(__file__)
# THE DUMMY settings.py BESIDE THIS FILE MUST WIN OVER ANY OTHER ON THE PATH
sys.path.insert(0, os.path.abspath(_here))
sys.path.insert(1, os.path.abspath(os.path.join(_here, '../../../../common')))
sys.path.insert(2, os.path.abspath(os.path.join(_here, '../../../../webserver/lasair')))
# annotate_util AND ITS NEIGHBOURS IMPORT EACH OTHER BY BARE NAME
sys.path.insert(3, os.path.abspath(os.path.join(_here, '../../../../common/src')))

