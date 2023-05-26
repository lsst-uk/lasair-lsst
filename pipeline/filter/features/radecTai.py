from features.CopyFeature import CopyFeature
  
class radecTai(CopyFeature):
  """MJD of latest detection"""

  # we need to override the default method because double is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "radecTai", "type": "float", "doc": "MJD of latest detection" }
