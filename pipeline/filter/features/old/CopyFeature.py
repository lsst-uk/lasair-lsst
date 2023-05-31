#import sys
#sys.path.append("../../../common/schema/lasair_schema")
#from objects import schema as objectSchema
from features.FeatureInterface import FeatureInterface

class CopyFeature(FeatureInterface):
  """Base class for features that simply copy a value"""

  @classmethod
  def run(cls, alert):
    """Generate the feature by copying from the alert"""
    name = cls.__name__
    object = alert.get("diaObject")
    return object.get(name)

