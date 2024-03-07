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
            idx = int(ra % 0.01 * 1000)
            at = associatationTypes.get(idx, 'ORPHAN')
            classifications[name] = [at, "This is a fake classification."]
            crossmatches.append({ "association_type": at, "transient_object_id": name })

        return classifications, crossmatches
