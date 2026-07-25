from fink_client.consumer import AlertConsumer

""" classifications, see https://lsst.fink-portal.org/schemas
CATS classifier broad class prediction with the highest probability. -1= not processed, 
11=SN-like, 
12=Fast (e.g. KN, ulens, Novae, ...), 
13=Long (e.g. SLSN, TDE, ...), 
21=Periodic (e.g. RRLyrae, EB, ...), 
22=Non-periodic (e.g. AGN). 
See https://arxiv.org/abs/2404.08798 Available from fink_broker_version 4.0 and fink_science_version 8.26.0.
"""

classes = {11: 'SN-like', 12: 'Fast', 13: 'Long', 21:'Periodic', 22:'NonPeriodic'}

class Annotator():
    def __init__(self, settings):
        self.settings = settings
        fink_config = {
            'username':          settings['USERNAME'] ,
            'bootstrap.servers': settings['SERVERS'],
            'group.id':          'bla15'
        }
        self.consumer = AlertConsumer([settings['MODULE']], fink_config)

    def next_ann(self):
        (topic, alert, version) = self.consumer.poll(10)
        if topic is None:
            return None

        diaObjectId = alert['diaSource']['diaObjectId']
        classdict = alert['clf']
        try:
            classification = classes[classdict['cats_class']]
        except:
            classification = 'Unknown'
        return {'diaObjectId'   : diaObjectId,
                'topic'         : 'fink_snn',
                'classification': classification,
                'classdict'     : classdict,
                }
