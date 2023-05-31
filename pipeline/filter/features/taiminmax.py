from features.FeatureGroup import FeatureGroup

class taiminmax(FeatureGroup):
  """Min and Max time of the diaSources"""

  _features = [
    "taimin",
    "taimax"
    ]  

  def run(self):
    taiList = [diaSource['midPointTai'] for diaSource in self.alert['diaSourcesList']]
    return { "taimin": min(taiList), "taimax": max(taiList) }

  # we need to override the default method because double is not a python type
  @classmethod
  def get_schema(cls) -> dict:
    """Get the schema for the feature output"""
    schema = {
      "taimin": {
        "name": "taimin",
        "type": "float",
        "doc": "Earliest MJD of a diaSource"
        },
      "taimax": {
        "name": "taimax",
        "type": "float",
        "doc": "Latest MJD of a diaSource"
        }
      }
    return schema


