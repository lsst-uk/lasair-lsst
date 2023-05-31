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

