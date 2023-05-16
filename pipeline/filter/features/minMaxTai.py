from FeatureInterface import FeatureInterface

class minMaxTai(FeatureInterface):
  """This is an example feature that always returns the value 1.23"""

  def get_schema(self) -> dict:
    schema = [{
      "name": "taimin",
      "type": "double"
    },{
      "name": "taimax",
      "type": "double"
    }]
    return schema

  def run(self, alert) -> dict:
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourceList']]
    return {
        "taimin": min(taiList),
        "taimax": max(taiList),
    }

