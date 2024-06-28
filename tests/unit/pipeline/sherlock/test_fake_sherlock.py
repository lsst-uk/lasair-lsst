import unittest, unittest.mock
import context
from fakeSherlock import transient_classifier

# some test values to use
ra = [ 100.001923, 100.004056, 100.004534, 100.0069223, 100.008056, 100.009034, 100.000186]
dec = [ 18.162226, 10.273649, 18.162388, 18.387237, -10.162002, 21.127438, 18.982293 ]
names = [ "yan", "tan", "tethera", "methera", "pip", "sethera", "lethera" ]
expected_classifications = {
    "yan": ['AGN', "This is a fake classification."],
    "tan": ['CV', "This is a fake classification."],
    "tethera": ['NT', "This is a fake classification."],
    "methera": ['SN', "This is a fake classification."],
    "pip": ['VS', "This is a fake classification."],
    "sethera": ['BS', "This is a fake classification."],
    "lethera": ['ORPHAN', "This is a fake classification."],
}
expected_crossmatches_by_name = {
    "lethera": {
        "transient_object_id": "lethera",
        "association_type": "ORPHAN",
        "z": None,
        "photoZ": None,
        "distance": None,
    },
    "yan": {
        "transient_object_id": "yan",
        "association_type": "AGN",
        "z": None,
        "photoZ": None,
        "distance": None,
    },
    "tan": {
        "transient_object_id": "tan",
        "association_type": "CV",
        "z": None,
        "photoZ": None,
        "distance": None,
    },
    "tethera": {
        "transient_object_id": "tethera",
        "association_type": "NT",
        "z": 0.007,
        "photoZ": 0.0438,
        "distance": 708.6,
    },
    "methera": {
        "transient_object_id": "methera",
        "association_type": "SN",
        "z": None,
        "photoZ": None,
        "distance": 14.6,
    },
    "pip": {
        "transient_object_id": "pip",
        "association_type": "VS",
        "z": None,
        "photoZ": None,
        "distance": None,
    },
    "sethera": {
        "transient_object_id": "sethera",
        "association_type": "BS",
        "z": None,
        "photoZ": None,
        "distance": None,
    },
}

class FakeSherlockTest(unittest.TestCase):
    """Fake Sherlock is a substitute Sherlock that produces fake (but deterministic)
    classifications using the same interface as the real Sherlock."""

    def test_classify(self):
        mock_log = unittest.mock.MagicMock()
        sherlock_settings = {}
        classifier = transient_classifier(
            log = mock_log,
            settings = sherlock_settings,
            ra = ra,
            dec = dec,
            name = names,
            verbose = 0,
            updateNed = False,
            lite = True
        )
        classifications, crossmatches = classifier.classify()
        # check content of classifications is as expected
        self.assertEqual(classifications, expected_classifications)
        # check content of crossmatches is as expected
        cm_by_name = {}
        for cm in crossmatches:
            name = cm["transient_object_id"]
            cm_by_name[name] = cm
            #self.assertEqual(cm, expected_crossmatches_by_name[name])
        self.assertEqual(cm_by_name, expected_crossmatches_by_name)
 

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
