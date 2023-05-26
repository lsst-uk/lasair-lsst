from features.FeatureInterface import FeatureInterface

class taimax(FeatureInterface):
  """Max time of the diaSources"""

  @classmethod
  def run(cls, alert):
    if not alert:
      return 0.0
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourcesList']]
    return max(taiList)

  # we need to override the default method because double is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "taimax", "type": "float", "doc": "Latest MJD of a diaSource" }

