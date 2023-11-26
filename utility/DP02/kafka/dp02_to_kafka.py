import csv, json
from confluent_kafka import Producer, KafkaError

def csv_to_list(dir):
    allObjects = []

    obj_stream = open(dir + '/diaObject.csv')

    for diaObject in csv.DictReader(obj_stream):
        diaObjectId = diaObject['diaObjectId']
        wholeObject = {
            'diaObject': diaObject, 
            'diaSource': [], 
            'diaForcedSource':[],
        }

        src_stream = open(dir + '/diaSource/%s.csv'%diaObjectId)
        for diaSource in csv.DictReader(src_stream):
            wholeObject['diaSource'].append(diaSource)

        fs_stream = open(dir + '/forcedSourceOnDiaObject/%s.csv'%diaObjectId)
        for diaForcedSource in csv.DictReader(fs_stream):
            wholeObject['diaForcedSource'].append(diaForcedSource)

        allObjects.append(wholeObject)
    return allObjects

if __name__ == '__main__':
    dir = '../data/data_0005_10'
    allObjects = csv_to_list(dir)

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)
    topic = 'DP02'
    for obj in allObjects:
        p.produce(topic, obj)
    p.flush()
