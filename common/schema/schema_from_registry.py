""" Fetches a schema from the schema registry
    Currently the registry is https://usdf-alert-schemas-dev.slac.stanford.edu
    Currently the only working schema_id is 1
"""
import os
import sys
import time
import json
from confluent_kafka.schema_registry import SchemaRegistryClient

SCHEMA_REG_URL = "https://usdf-alert-schemas-dev.slac.stanford.edu"

if len(sys.argv) > 1:
    schema_id = int(sys.argv[1])
else:
    schema_id = 1

sr_client = SchemaRegistryClient({"url": SCHEMA_REG_URL})
schema = sr_client.get_schema(schema_id=schema_id)
s = json.loads(schema.schema_str)
print(json.dumps(s, indent=2))

