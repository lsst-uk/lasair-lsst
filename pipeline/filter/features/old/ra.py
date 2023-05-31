from features.CopyFeature import CopyFeature
  
class ra(CopyFeature):
  """Mean RA of this object"""

  # we need to override the default method because double is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "ra", "type": "float", "doc": "Mean RA of this object" }
