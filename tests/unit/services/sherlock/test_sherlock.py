import os, sys, json
import unittest, unittest.mock
import context
from app import app

class SherlockServiceTest(unittest.TestCase):
    """
    Unit tests for the Sherlock service.
    See https://flask.palletsprojects.com/en/latest/testing/ for information on app.test_client()

    These tests currently just test the API and validation code, not the Sherlock or Database interfaces.
    """

    def test_get_query_single(self):
        """
        Check that a GET on a single point returns whatever classify gives it.
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "foo": [ "SN", "blah" ] },[{ "bar": 0.12 }])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.get("/query?ra=1&dec=2")
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")

    def test_post_query_single(self):
        """
        Check that a POST on a single point returns whatever classify gives it.
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "foo": [ "SN", "blah" ] },[{ "bar": 0.12 }])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "dec": 1.2, "ra": 2.3 })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")

    def test_query_multi(self):
        """
        Check that lists of queries work.
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "one": [ "SN", "blah" ], "two": [ "AGN", "blah" ] },[{}])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "dec": "1.2,2.3", "ra": "2.3,3.4", "name": "one,two" })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")

    def test_query_lite(self):
        """
        Check that passing lite=True works
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "foo": [ "SN", "blah" ] },[{}])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "dec": 1.2, "ra": 2.3, "lite": "True" })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")

    def test_query_named(self):
        """
        Check that passing a name works
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "bar+0": [ "SN", "blah" ] },[{}])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "dec": 1.2, "ra": 2.3, "name": "bar+0" })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")

    def test_query_invalid_dec(self):
        """
        Check that passing an invalid value for dec gives a 400 error.
        """
        client = app.test_client()
        response = client.post("/query", json={ "dec": "xyz", "ra": 2.3 })
        self.assertEqual(response.status_code, 400)

    def test_query_invalid_ra(self):
        """
        Check that passing an invalid value for ra gives a 400 error.
        """
        client = app.test_client()
        response = client.post("/query", json={ "dec": "1.2", "ra": -2 })
        self.assertEqual(response.status_code, 400)

    def test_query_invalid_name(self):
        """
        Check that passing an invalid value for name gives a 400 error.
        """
        client = app.test_client()
        response = client.post("/query", json={ "dec": "1.2", "ra": "2", "name": "as2;df" })
        self.assertEqual(response.status_code, 400)

    def test_query_wrong_list_length(self):
        """
        Check that passing different length lists gives a 400 error.
        """
        client = app.test_client()
        response = client.post("/query", json={ "dec": "1.2,34", "ra": "100.1" })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
