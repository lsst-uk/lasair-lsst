from features.CopyFeature import CopyFeature
  
class decl(CopyFeature):
  """Mean Dec of this object"""

  # we need to override the default method because double is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "decl", "type": "float", "doc": "Mean Dec of this object" }
