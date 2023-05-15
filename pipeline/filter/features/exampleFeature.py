from FeatureInterface import FeatureInterface

class exampleFeature(FeatureInterface):
  """This is an example feature that always returns the value 1.23"""

  def get_schema(self) -> dict:
    schema = {
      "name": "exampleFeature",
      "type": "double"
    }
    return schema

  def run(self, alert) -> dict:
    return 1.23

