from features.CopyFeature import CopyFeature
  
class diaObjectId(CopyFeature):
  """diaObjectID is the primary key"""

  # we need to override the default method because long is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    return { "name": "diaObjectId", "type": "int", "extra": "NOT NULL" }

#  @classmethod
#  def run(cls, alert):
#    # do something
#    return "2"

