from features.FeatureGroup import FeatureGroup

class timing(FeatureGroup):
    """Min and Max time of the diaSources"""

    _features = [
        "nDiaSources",
        "minTai",
        "maxTai"
    ]    

    def run(self):
        taiList = [diaSource['midPointTai'] for diaSource in self.alert['diaSourcesList']]
        return { 
            "nDiaSources": len(taiList),
            "minTai"     : min(taiList), 
            "maxTai"     : max(taiList),
        }
