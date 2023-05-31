from features.FeatureInterface import FeatureInterface
import time

class ncand_7(FeatureInterface):
  """Number of diaSource in light curve in last 7 days"""

  @classmethod
  def _mjd_now(cls):
    """ *return the current UTC time as an MJD* """
    return time.time() / 86400 + 40587.0

  @classmethod
  def run(cls,alert=None):
    """Number of diaSources -- last 7 days """
    if not alert:
      return 0
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourcesList']]
    taiNow = cls._mjd_now()
    ncand_7 = 0
    for tai in taiList:
        if tai > taiNow -7:
            ncand_7 += 1
    return ncand_7

