from features.FeatureGroup import FeatureGroup

class tns(FeatureGroup):
    """Put in an empty entry for the tns_name that will be filled in later"""

    _features = [
        "tns_name",
    ]    

    def run(self):
        return { 
            "tns_name": '', 
        }
