import os, sys, json
import unittest, unittest.mock
import context
from app import app, NotFoundException

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
            test_data = ({ "query0": [ "SN", "blah" ] },[{ "bar": 0.12 }])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.get("/query?ra=1.1&dec=2")
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")
            mock_classify.assert_called_once_with(["query0"], [1.1], [2.0], False)

    def test_post_query_single(self):
        """
        Check that a POST on a single point returns whatever classify gives it.
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "query0": [ "SN", "blah" ] },[{ "bar": 0.12 }])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "ra": 1.2, "dec": 2.3 })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")
            mock_classify.assert_called_once_with(["query0"], [1.2], [2.3], False)

    def test_query_multi(self):
        """
        Check that lists of queries work.
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "query0": [ "SN", "blah" ], "query1": [ "AGN", "blah" ] },[{}])
            mock_classify.return_value = test_data
            client = app.test_client()
            response = client.post("/query", json={ "ra": "1.2,2.3", "dec": "2.3,3.4" })
            try:
                # the response we get back should be whatever classify returned
                response_data = response.json
                self.assertEqual(test_data[0], response_data['classifications'])
                self.assertEqual(test_data[1], response_data['crossmatches'])
            except Exception as e:
                # if the response doesn't decode as json it's probably an error that we'd like to see
                self.fail(f"Response: {response.status}: {response.text}")
            mock_classify.assert_called_once_with(["query0", "query1"], [1.2, 2.3], [2.3, 3.4], False)

    def test_query_lite(self):
        """
        Check that passing lite=True works
        """
        with unittest.mock.patch('app.classify') as mock_classify:
            test_data = ({ "query0": [ "SN", "blah" ] },[{}])
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
            mock_classify.assert_called_once_with(["query0"], [2.3], [1.2], True)

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
            mock_classify.assert_called_once_with(["bar+0"], [2.3], [1.2], False)

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

    def test_object(self):
        """
        Check get for a single object
        """
        with unittest.mock.patch('app.lookup') as mock_lookup:
            mock_lookup.return_value = ([1], [2])
            with unittest.mock.patch('app.classify') as mock_classify:
                test_data = ({ "foo": [ "SN", "blah" ] },[{ "bar": 0.12 }])
                mock_classify.return_value = test_data
                client = app.test_client()
                response = client.get("/object/foo")
                try:
                    # the response we get back should be whatever classify returned
                    response_data = response.json
                    self.assertEqual(test_data[0], response_data['classifications'])
                    self.assertEqual(test_data[1], response_data['crossmatches'])
                except Exception as e:
                    # if the response doesn't decode as json it's probably an error that we'd like to see
                    self.fail(f"Response: {response.status}: {response.text}")
                # check that lookup and classify got called ok
                mock_lookup.assert_called_once_with(["foo"])
                mock_classify.assert_called_once_with(["foo"], [1], [2], False)

    def test_object_multi(self):
        """
        Check get for a list of objects
        """
        with unittest.mock.patch('app.lookup') as mock_lookup:
            mock_lookup.return_value = ([1, 3], [2, 4])
            with unittest.mock.patch('app.classify') as mock_classify:
                test_data = ({ "foo": [ "SN", "blah" ], "bar": [ "AGN", "blah" ] },[{ }])
                mock_classify.return_value = test_data
                client = app.test_client()
                response = client.get("/object/foo,bar")
                try:
                    # the response we get back should be whatever classify returned
                    response_data = response.json
                    self.assertEqual(test_data[0], response_data['classifications'])
                    self.assertEqual(test_data[1], response_data['crossmatches'])
                except Exception as e:
                    # if the response doesn't decode as json it's probably an error that we'd like to see
                    self.fail(f"Response: {response.status}: {response.text}")
                # check that lookup and classify got called ok
                mock_lookup.assert_called_once_with(["foo", "bar"])
                mock_classify.assert_called_once_with(["foo", "bar"], [1, 3], [2, 4], False)

    def test_object_lite(self):
        """
        Check object with lite=true
        """
        with unittest.mock.patch('app.lookup') as mock_lookup:
            mock_lookup.return_value = ([1], [2])
            with unittest.mock.patch('app.classify') as mock_classify:
                test_data = ({ "foo": [ "SN", "blah" ] },[{ "bar": 0.12 }])
                mock_classify.return_value = test_data
                client = app.test_client()
                response = client.post("/object/foo", json={ "lite": "True" })
                try:
                    # the response we get back should be whatever classify returned
                    response_data = response.json
                    self.assertEqual(test_data[0], response_data['classifications'])
                    self.assertEqual(test_data[1], response_data['crossmatches'])
                except Exception as e:
                    # if the response doesn't decode as json it's probably an error that we'd like to see
                    self.fail(f"Response: {response.status}: {response.text}")
                # check that lookup and classify got called ok
                mock_lookup.assert_called_once_with(["foo"])
                mock_classify.assert_called_once_with(["foo"], [1], [2], True)

    def test_object_invalid(self):
        """
        Check object with a bad name returns 400
        """
        client = app.test_client()
        response = client.post("/object/f^oo")
        self.assertEqual(response.status_code, 400)

    def test_object_not_found(self):
        """
        Check object not found returns 404
        """
        with unittest.mock.patch('app.lookup') as mock_lookup:
            mock_lookup.side_effect = NotFoundException("test")
            client = app.test_client()
            response = client.post("/object/foo")
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
