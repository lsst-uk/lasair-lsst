from features.FeatureInterface import FeatureInterface

class ncand(FeatureInterface):
  """Number of diaSource in light curve"""

  @classmethod
  def run(cls,alert=None):
    """Number of diaSources -- all"""
    if not alert:
      return 0
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourcesList']]
    return len(taiList)

