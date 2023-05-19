import sys
sys.path.append("../../../common/schema/lasair_schema")
from diaObjects import schema as objectSchema

class FeatureInterface:
  """Interface used by feature processors"""

  @classmethod
  def get_info(cls) -> str:
    """Get a string with information about the schema"""
    # use the "doc" entry from the schema if it exists, otherwise use the docstring
    return cls.get_schema().get("doc", cls.__doc__)

  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    for feature in objectSchema['fields']:
      name = feature['name']
      if name == cls.__name__:
        return feature

  @classmethod
  def run(cls, alert) -> dict:
    """Generate the feature for the given alert"""
    pass

