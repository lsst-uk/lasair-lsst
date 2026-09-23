import json
from fink_client.consumer import AlertConsumer
from proxy_annotators import ProxyAnnotator

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


class Annotator(ProxyAnnotator):
    def __init__(self, settings):
        super().__init__(settings)
        if 'group_id' in settings:
            group_id = settings['group_id']
        else:
            group_id = 'bla15'
        fink_config = {
            'username':          settings['USERNAME'] ,
            'bootstrap.servers': settings['SERVERS'],
            'group.id':          group_id,
        }
        self.consumer = AlertConsumer([settings['MODULE']], fink_config)

    def next_ann(self):
        (topic, alert, version) = self.consumer.poll(10)
        if topic is None:
            return {'error': 'End of stream'}

        if self.settings['verbose']:
            result = {'info': f'Got record {str(record)}'}
        else:
            result = {}

        diaObjectId = alert['diaSource']['diaObjectId']
        classdict = alert['clf']
        try:
            classification = classes[classdict['cats_class']]
        except:
            classification = 'Unknown'
        result['annotation'] = {'diaObjectId'   : diaObjectId,
                'topic'         : 'fink_snn',
                'classification': classification,
                'classdict'     : json.dumps(classdict),
                }
        return result
