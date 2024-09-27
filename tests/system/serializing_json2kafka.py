import os, sys, json, io, gzip
import fastavro
from confluent_kafka import SerializingProducer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import base64

SCHEMA_REG_URL = "https://usdf-alert-schemas-dev.slac.stanford.edu"
# use sr_client.get_subjects() 
SCHEMA_SUBJECT = "alert-packet"
# use sr_client.get_versions('alert-packet')
SCHEMA_VERSION = 701

def subject_name(context, string):
    return SCHEMA_SUBJECT
    ##return f"{ SCHEMA_SUBJECT }/versions/{ SCHEMA_VERSION }"

def encode_cutouts(data):
    names = ['cutoutDifference', 'cutoutScience', 'cutoutTemplate']
    for name in names:
        if data.get(name):
            data[name] = base64.b64decode(data[name])


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        broker = sys.argv[1]
        datafile = sys.argv[2]
        topic = sys.argv[3]
    else:
        print('Usage: json_to_kafka.py <broker> <file> <topic>')
        sys.exit()

    #schemafile = '../../common/schema/dp02.avsc'
    #schema = json.loads(open(schemafile).read())
    #parsed_schema = fastavro.parse_schema(schema)

    sr_client = SchemaRegistryClient({"url": SCHEMA_REG_URL})
    reg_schema = sr_client.get_version(SCHEMA_SUBJECT, SCHEMA_VERSION)

    conf = {
        "auto.register.schemas": False,
        "normalize.schemas": False,
        "use.latest.version": False,
        "subject.name.strategy": subject_name
        }

    serializer = AvroSerializer(sr_client, reg_schema.schema, conf=conf)
    AvroSerializer._schema_id = reg_schema.schema_id
    AvroSerializer._known_subjects = set({ SCHEMA_SUBJECT })

    conf = {
        "bootstrap.servers": broker,
        "client.id": "client-1",
        "value.serializer": serializer
    }
    p = SerializingProducer(conf)

    with open(datafile, 'r') as fin:
        obj = json.load(fin)          
        encode_cutouts(obj)
        p.produce(topic, value=obj)
        p.flush()

