"""
This code reads sample alerts, each is a ZTF alert, with cutouts removed, 
and Sherlock annotation added. It converts these to SQL INSERT ot REPLACE
queries by computing features, then writes the queries.
Input:  name.json
Output: name.sql
"""
import unittest.main
from unittest import TestCase, expectedFailure
import json
import os
import sys
import context
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../pipeline/filter/features_ZTF')))
from insert_query import create_insert_query, create_insert_annotation

# the expected attributes in the 'sherlock' annotation
sherlock_attributes = [
    "classification",
    "objectId",
    "association_type",
    "catalogue_table_name",
    "catalogue_object_id",
    "catalogue_object_type",
    "raDeg",
    "decDeg",
    "separationArcsec",
    "northSeparationArcsec",
    "eastSeparationArcsec",
    "physical_separation_kpc",
    "direct_distance",
    "distance",
    "z",
    "photoZ",
    "photoZErr",
    "Mag",
    "MagFilter",
    "MagErr",
    "classificationReliability",
    "major_axis_arcsec",
    "annotator",
    "additional_output",
    "description",
    "summary",
]

# for each file in the sample_alerts, build the features and query
class FilterMakeFeaturesTest(TestCase):

    def test_make_features(self):
        for filename in os.listdir('sample_alerts'):
            filename = filename.split('.')[0]
#            print('\n' + filename)
            alert = json.loads(open('sample_alerts/%s.json' % filename).read())
            objectId = alert['objectId']

            computed_output = ''
            querydict = create_insert_query(alert)
            if querydict and 'query' in querydict:
                query = querydict['query']
                computed_output += query + ';\n\n'
#                queryfile = open('sample_queries/%s.sql' % filename, 'w')
#                queryfile.write(computed_output)
            else:
                print('%s: No query created' % filename)
                break

            # look for any queries labelled 'sherlock'
            if 'annotations' in alert:
                annotations = alert['annotations']
                annClass = 'sherlock'
                for ann in annotations[annClass]:
                    if "transient_object_id" in ann:  # hack here. Sherlock and Lasair have different names
                        ann['objectId'] = ann.pop('transient_object_id')

                    query = create_insert_annotation(objectId, annClass, ann,
                        sherlock_attributes, 'sherlock_classifications', replace=True)
                    computed_output += query + ';\n\n'
#                    queryfile.write(query +';\n\n')

#            queryfile.close()
            stored_output = open('sample_queries/%s.sql' % filename, 'r').read()
            self.assertTrue(computed_output == stored_output)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()

