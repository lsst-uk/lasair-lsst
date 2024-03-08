import math
import random

class transient_classifier():

    def __init__(self,
        log,
        settings=False,
        update=False,
        ra=False,
        dec=False,
        name=False,
        verbose=0,
        updateNed=True,
        daemonMode=False,
        updatePeakMags=True,
        oneRun=False,
        lite=False
        ):
        self.log = log
        self.ra = ra
        self.dec = dec
        self.name = name

    def classify(self):
        classifications = {}
        crossmatches = []

        associatationTypes = { 1: "AGN", 2: "CV", 3: "NT", 4: "SN", 5: "VS", 6:"BS" }

        for i in range(len(self.name)):
            name = self.name[i]
            ra= self.ra[i]
            dec = self.dec[i]

            # pick an association type based on the ra
            idx = int((ra % 0.01) * 700)
            at = associatationTypes.get(idx, 'ORPHAN')
            classifications[name] = [at, "This is a fake classification."]

            # seed the rng using the dec
            random.seed(int((dec % 1) * 1000))

            # if SN or NT get a random distance/z/photoZ
            dist = z = photoZ = None
            if at == 'SN' or at == 'NT':
                if random.random() < 0.5:
                    dist = round(math.exp(random.uniform(2.5,7)),1)
                if random.random() < 0.5:
                    z = round(0.00023 * math.exp(random.uniform(2.5,7)),4)
                if random.random() < 0.5:
                    photoZ = round(0.00023 * math.exp(random.uniform(2.5,7)),4)
            
            crossmatches.append({
                "association_type": at,
                "transient_object_id": name,
                "distance": dist,
                "z": z,
                "photoZ": photoZ,
                })

        return classifications, crossmatches

