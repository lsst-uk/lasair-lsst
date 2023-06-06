from features.FeatureGroup import FeatureGroup

class sherlock(FeatureGroup):
    """Features that need the sherlock packet"""

    _features = [
        "absFlux",
    ]    

    def run(self):
        absFlux = None
        if 'annotations' in self.alert:
            annotations = self.alert['annotations']
            if 'sherlock' in annotations:
                ann = alert['annotations'][sherlock]
                if 'blabla' in ann:
                    # figure out absolute flux
                    absFlux = 100
                    
        return { 
            "absFlux": absFlux, 
        }

