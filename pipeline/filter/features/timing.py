from features.FeatureGroup import FeatureGroup

class timing(FeatureGroup):
    """Min and Max time of the diaSources"""

    _features = [
        "taiMin",
        "taiMax"
    ]    

    def run(self):
        taiList = [diaSource['midPointTai'] for diaSource in self.alert['diaSourcesList']]
        return { 
            "taiMin": min(taiList), 
            "taiMax": max(taiList),
        }
