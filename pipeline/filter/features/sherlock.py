from features.FeatureGroup import FeatureGroup

class sherlock(FeatureGroup):
    """Features that need the sherlock packet"""

    _features = [
        "absoluteFlux",
    ]    

    def run(self):
        absoluteFlux = None
        if 'annotations' in alert:
            annotations = alert['annotations']
            if 'sherlock' in annotations:
                ann = alert['annotations'][sherlock]:
                if 'blabla' in ann:
                    # figure out absolute flux
                    absoluteFlux = 100
                    
        return { 
            "absoluteFlux": absoluteFlux, 
        }

