from features.FeatureInterface import FeatureInterface
  
class htm16(FeatureInterface):
  """Hierarchical Triangular Mesh level 16"""

  # we need to override the default method because bigint is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "htm16", "type": "int", "doc": "Hierarchical Triangular Mesh level 16", "extra": "NOT NULL" }

  @classmethod
  def run(cls, alert):
    """Compute the htm16"""
    # use the htm16 from the latest diaSource if available
    diaSources = alert.get("diaSourcesList", [])
    diaSource = diaSources[0] if len(diaSources) else None
    if diaSource:
      return diaSource.get('htm16')
    else:
      # should calculate it if necessary
      return None 
