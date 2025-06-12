import unittest
import unittest.mock
from unittest.mock import call
import logging
import sys
import json

import context
import wrapper
from confluent_kafka import KafkaError, KafkaException
from pkg_resources import get_distribution

log = logging.getLogger()
log.level = logging.WARN
# log.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)

with open("sample_alerts/single_alert_batch.json", 'r') as f:
    data = json.load(f)
    example_alert = data[0]
    example_input_data = json.dumps(data[0])

with open("sample_alerts/singleton.json", 'r') as f:
    data = json.load(f)
    example_singleton = data[0]


class MockMessage:
    """mock kafka message class for use by mock poll"""
    def __init__(self, err=None):
        self.err = err

    @staticmethod
    def value():
        return example_input_data

    def error(self):
        return self.err

    @staticmethod
    def offset():
        return 0


nfe_call_count = 0
def non_fatal_error_on_1st_call(timeout):
    """mock poll method that returns an error the 1st time called"""
    global nfe_call_count
    nfe_call_count += 1
    if nfe_call_count > 1:
        return MockMessage()
    else:
        e = KafkaError(KafkaError._APPLICATION, "Test Error", fatal=False, retriable=True)
        return MockMessage(e)


class SherlockWrapperConsumerTest(unittest.TestCase):

    conf = {
        'broker': '',
        'group': '',
        'input_topic': '',
        'output_topic': '',
        'batch_size': 5,
        'timeout': 1,
        'max_errors': -1,
        'cache_db': '',
        'poll_timeout': 1,
        'max_poll_interval': 300000
        }

    def test_consume_end_of_topic(self):
        """test consumer reaching end of topic"""
        with unittest.mock.MagicMock() as mock_kafka_consumer:
            mock_kafka_consumer.poll.return_value = None
            alerts = []
            # consume should report consuming 0 alerts
            self.assertEqual(wrapper.consume(self.conf, log, alerts, mock_kafka_consumer), 0)
            # alerts should be empty
            self.assertEqual(alerts, [])
            # poll should have been called once with timeout 1
            mock_kafka_consumer.poll.assert_called_once_with(1)

    def test_consume_alert_batch(self):
        """test consuming a batch of alerts"""
        with unittest.mock.patch('wrapper.classify') as mock_classify:
            with unittest.mock.patch('wrapper.produce') as mock_produce:
                with unittest.mock.MagicMock() as mock_kafka_consumer:
                    mock_classify.return_value = 5
                    mock_produce.return_value = 5
                    mock_kafka_consumer.poll.return_value.error.return_value = None
                    mock_kafka_consumer.poll.return_value.value.return_value = example_input_data
                    alerts = []
                    # consume should report consuming 5 alerts
                    self.assertEqual(wrapper.consume(self.conf, log, alerts, mock_kafka_consumer), 5)
                    # alerts should have len 5
                    self.assertEqual(len(alerts), 5)
                    # content of alerts should be as expected
                    self.assertEqual(alerts[0]['diaObject']['ra'], 155.06611633096068)
                    # poll should have been called 5 times
                    self.assertEqual(mock_kafka_consumer.poll.call_count, 5)

    def test_fatal_error(self):
        """test that a fatal error is fatal"""
        with unittest.mock.MagicMock() as mock_kafka_consumer:
            # poll returns None when no messages left to consume
            e = KafkaError(KafkaError._FATAL, "Test Error", fatal=True, retriable=False)
            mock_kafka_consumer.poll.return_value.error.return_value = e
            mock_kafka_consumer.poll.return_value.value.return_value = example_input_data
            alerts = []
            # consume should report consuming 0 alerts
            self.assertEqual(wrapper.consume(self.conf, log, alerts, mock_kafka_consumer), 0)
            # alerts should be empty
            self.assertEqual(alerts, [])
            # poll should have been called once with timeout 1
            mock_kafka_consumer.poll.assert_called_once_with(1)

    def test_non_fatal_error(self):
        """test that a non-fatal error is non-fatal"""
        with unittest.mock.patch('wrapper.classify') as mock_classify:
            with unittest.mock.patch('wrapper.produce') as mock_produce:
                with unittest.mock.MagicMock() as mock_kafka_consumer:
                    mock_classify.return_value = 5
                    mock_produce.return_value = 5
                    # poll returns None when no messages left to consume
                    mock_kafka_consumer.poll = non_fatal_error_on_1st_call
                    alerts = []
                    # consume should report consuming 0 alerts
                    self.assertEqual(wrapper.consume(self.conf, log, alerts, mock_kafka_consumer), 5)
                    # alerts should have len 5
                    self.assertEqual(len(alerts), 5)
                    # content of alerts should be as expected
                    self.assertEqual(alerts[0]['diaObject']['ra'], 155.06611633096068)
                    # poll should have been called 6 times
                    self.assertEqual(nfe_call_count, 6)

    def test_max_errors(self):
        """test max non-fatal errors"""
        with unittest.mock.MagicMock() as mock_kafka_consumer:
            # poll returns None when no messages left to consume
            e = KafkaError(KafkaError._APPLICATION, "Test Error", fatal=False, retriable=True)
            mock_kafka_consumer.poll.return_value.error.return_value = e
            mock_kafka_consumer.poll.return_value.value.return_value = example_input_data
            conf = {
                'broker': '',
                'group': '',
                'input_topic': '',
                'output_topic': '',
                'batch_size': 5,
                'timeout': 1,
                'max_errors': 1,
                'cache_db': '',
                'poll_timeout': 1,
                'max_poll_interval': 300000
                }
            alerts = []
            # consume should report consuming 0 alerts
            self.assertEqual(wrapper.consume(conf, log, alerts, mock_kafka_consumer), 0)
            # alerts should be empty
            self.assertEqual(alerts, [])
            # poll should have been called twice with timeout 1
            # (poll.error will also have been called several times)
            mock_kafka_consumer.poll.assert_has_calls([call(1), call(1)], any_order=True)

    def test_failed_commit(self):
        """test (non-fatal) failure on commit"""
        with unittest.mock.patch('wrapper.classify') as mock_classify:
            with unittest.mock.patch('wrapper.produce') as mock_produce:
                with unittest.mock.MagicMock() as mock_kafka_consumer:
                    mock_classify.return_value = 5
                    mock_produce.return_value = 5
                    mock_kafka_consumer.poll.return_value.error.return_value = None
                    mock_kafka_consumer.poll.return_value.value.return_value = example_input_data
                    e = KafkaError(KafkaError._NO_OFFSET, 'test no offset', fatal=False)
                    mock_kafka_consumer.commit.side_effect = KafkaException(e)
                    alerts = []
                    # consume should report consuming 5 alerts
                    self.assertEqual(wrapper.consume(self.conf, log, alerts, mock_kafka_consumer), 5)
                    # alerts should have len 5
                    self.assertEqual(len(alerts), 5)
                    # content of alerts should be as expected
                    self.assertEqual(alerts[0]['diaObject']['ra'], 155.06611633096068)

    def test_fatal_failed_commit(self):
        """test (non-fatal) failure on commit"""
        with unittest.mock.patch('wrapper.classify') as mock_classify:
            with unittest.mock.patch('wrapper.produce') as mock_produce:
                with unittest.mock.MagicMock() as mock_kafka_consumer:
                    mock_classify.return_value = 5
                    mock_produce.return_value = 5
                    mock_kafka_consumer.poll.return_value.error.return_value = None
                    mock_kafka_consumer.poll.return_value.value.return_value = example_input_data
                    e = KafkaError(KafkaError._NO_OFFSET, 'test no offset', fatal=True)
                    mock_kafka_consumer.commit.side_effect = KafkaException(e)
                    alerts = []
                    # consume should raise an exception
                    with self.assertRaises(Exception):
                        wrapper.consume(self.conf, log, alerts, mock_kafka_consumer)
                    # alerts should have len 5
                    self.assertEqual(len(alerts), 5)

    def test_exception_on_poll(self):
        """test (non-fatal) failure on commit"""
        with unittest.mock.MagicMock() as mock_kafka_consumer:
            e = KafkaError(KafkaError._NO_OFFSET, 'test no offset', fatal=True)
            mock_kafka_consumer.poll.return_value.error.return_value = e
            mock_kafka_consumer.poll.return_value.value.return_value = None
            mock_kafka_consumer.poll.side_effect = KafkaException(e)
            alerts = []
            # consume should raise an exception
            with self.assertRaises(Exception):
                wrapper.consume(self.conf, log, alerts, mock_kafka_consumer)


class SherlockWrapperClassifierTest(unittest.TestCase):
    crossmatches = [{
                    'rank': 1,
                    'transient_object_id': "177218944862519874",
                    'association_type': 'SN',
                    'catalogue_table_name': 'NED D/SDSS',
                    'catalogue_object_id': 'NGC0716',
                    'catalogue_object_type': 'galaxy',
                    'raDeg': 155.066116,
                    'decDeg': -3.970923,
                    'separationArcsec': 31.06,
                    'northSeparationArcsec': -16.204,
                    'eastSeparationArcsec': -26.493,
                    'physical_separation_kpc': 8.52,
                    'direct_distance': 56.6,
                    'distance': 65.88,
                    'z': 0.02,
                    'photoZ': 0.02,
                    'photoZErr': 0.01,
                    'Mag': 17.41,
                    'MagFilter': 'r',
                    'MagErr': 0.0,
                    'classificationReliability': 2}]

    def test_classify_alert_batch(self):
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': '',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            alerts = [example_alert.copy()]
            classifications = {"177218944862519874": ["Q"]}
            crossmatches = SherlockWrapperClassifierTest.crossmatches
            mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
            # should report classifying 1 alert
            self.assertEqual(wrapper.classify(conf, log, alerts), 1)
            # length of alerts should still be 1
            self.assertEqual(len(alerts), 1)
            # content of alerts should be as expected
            self.assertRegex(alerts[0]['annotations']['sherlock'][0]['annotator'],
                             "^https://github.com/thespacedoctor/sherlock")
            self.assertEqual(alerts[0]['annotations']['sherlock'][0]['additional_output'],
                             "http://lasair-lsst.lsst.ac.uk/api/sherlock/object/177218944862519874")
            self.assertEqual(alerts[0]['annotations']['sherlock'][0]['classification'], 'Q')
            for key, value in crossmatches[0].items():
                if key != 'rank':
                    self.assertEqual(alerts[0]['annotations']['sherlock'][0][key], value)
            # classify should have been called once
            mock_classifier.return_value.classify.assert_called_once()

    def test_classify_singleton(self):
        """Test that an alert with only one source gets ignored when ignore_singletons option is true."""
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': '',
            'sherlock_settings': 'sherlock_test.yaml',
            'ignore_singletons': True
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            alerts = [example_singleton.copy()]
            mock_classifier.return_value.classify.return_value = ({}, [])
            # should report classifying 0 alert
            self.assertEqual(wrapper.classify(conf, log, alerts), 0)
            # length of alerts should still be 1
            self.assertEqual(len(alerts), 1)
            # alert should not have a Sherlock annotation
            self.assertNotIn('sherlock', alerts[0].get('annotations', []))
            # classify should have been called once
            mock_classifier.return_value.classify.assert_not_called()

    def test_classify_description(self):
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': '',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            alerts = [example_alert.copy()]
            classifications = {"177218944862519874": ["Q", "Descr"]}
            crossmatches = SherlockWrapperClassifierTest.crossmatches
            mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
            # should report classifying 1 alert
            self.assertEqual(wrapper.classify(conf, log, alerts), 1)
            # content of alerts should be as expected
            self.assertEqual(alerts[0]['annotations']['sherlock'][0]['description'], 'Descr')

    def test_classify_cache_hit(self):
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': 'mysql://user_name:password@localhost:3306/sherlock_cache',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            with unittest.mock.patch('wrapper.pymysql.connect') as mock_pymysql:
                sherlock_version = get_distribution("qub-sherlock").version
                alerts = [example_alert.copy()]
                classifications = {"177218944862519874": ["QY", "Test"]}
                crossmatches = [{'transient_object_id': "177218944862519874", 'thing': 'foo'}]
                mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
                cache = [{'name': '177218944862519874', 'version': sherlock_version, 'class': 'T', 'description': 't',
                          'crossmatch': json.dumps(SherlockWrapperClassifierTest.crossmatches[0])}]
                mock_pymysql.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = cache
                # should report classifying 1 alert
                self.assertEqual(wrapper.classify(conf, log, alerts), 1)
                # length of alerts should still be 1
                self.assertEqual(len(alerts), 1)
                # content of alerts should be as expected - from cache
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['classification'], 'T')
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['description'], 't')
                self.assertRegex(alerts[0]['annotations']['sherlock'][0]['annotator'],
                                 "^https://github.com/thespacedoctor/sherlock")
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['additional_output'],
                                 "http://lasair-lsst.lsst.ac.uk/api/sherlock/object/177218944862519874")
                for key, value in SherlockWrapperClassifierTest.crossmatches[0].items():
                    if key != 'rank':
                        self.assertEqual(alerts[0]['annotations']['sherlock'][0][key], value)
                # classify should not have been called
                mock_classifier.return_value.classify.assert_not_called()

    def test_classify_cache_wrong_version(self):
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': 'mysql://user_name:password@localhost:3306/sherlock_cache',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            with unittest.mock.patch('wrapper.pymysql.connect') as mock_pymysql:
                alerts = [example_alert.copy()]
                classifications = {"177218944862519874": ["QU", "Desc"]}
                crossmatches = [{'transient_object_id': "177218944862519874", 'thing': 'foo'}]
                mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
                cache = [{'name': '177218944862519874', 'version': 'blah', 'class': 'T', 'description': 't',
                          'crossmatch': json.dumps(SherlockWrapperClassifierTest.crossmatches[0])}]
                mock_pymysql.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = cache
                # should report classifying 1 alert
                self.assertEqual(wrapper.classify(conf, log, alerts), 1)
                # content of alerts should be from sherlock - cache should be ignored
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['classification'], 'QU')
                # classify *should* have been called
                mock_classifier.return_value.classify.assert_called_once()

    def test_classify_cache_empty_hit(self):
        """check that if we get a cache hit but the crossmatch is empty/malformed then we ignore it"""
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': 'mysql://user_name:password@localhost:3306/sherlock_cache',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            with unittest.mock.patch('wrapper.pymysql.connect') as mock_pymysql:
                alerts = [example_alert.copy()]
                classifications = {"177218944862519874": ["QX", "A test"]}
                crossmatches = [{'transient_object_id': "177218944862519874", 'thing': 'foo'}]
                mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
                cache = [{'name': '177218944862519874', 'class': 'T', 'crossmatch': None}]
                mock_pymysql.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = cache
                # should report classifying 1 alert
                self.assertEqual(wrapper.classify(conf, log, alerts), 1)
                # content of alerts should be from sherlock - cache should be ignored
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['classification'], 'QX')
                # classify *should* have been called
                mock_classifier.return_value.classify.assert_called_once()

    def test_classify_cache_miss(self):
        conf = {
            'broker': '',
            'group': '',
            'input_topic': '',
            'output_topic': '',
            'batch_size': 5,
            'timeout': 1,
            'max_errors': -1,
            'cache_db': 'mysql://user_name:password@localhost:3306/sherlock_cache',
            'sherlock_settings': 'sherlock_test.yaml'
            }
        with unittest.mock.patch('wrapper.transient_classifier') as mock_classifier:
            with unittest.mock.patch('wrapper.pymysql.connect') as mock_pymysql:
                alerts = [example_alert.copy()]
                classifications = {"177218944862519874": ["QZ", "Desc"]}
                crossmatches = SherlockWrapperClassifierTest.crossmatches
                mock_classifier.return_value.classify.return_value = (classifications, crossmatches)
                mock_pymysql.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []
                # should report classifying 1 alert
                self.assertEqual(wrapper.classify(conf, log, alerts), 1)
                # length of alerts should still be 1
                self.assertEqual(len(alerts), 1)
                # content of alerts should be as expected - from sherlock
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['classification'], 'QZ')
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['description'], 'Desc')
                self.assertRegex(alerts[0]['annotations']['sherlock'][0]['annotator'],
                                 "^https://github.com/thespacedoctor/sherlock")
                self.assertEqual(alerts[0]['annotations']['sherlock'][0]['additional_output'],
                                 "http://lasair-lsst.lsst.ac.uk/api/sherlock/object/177218944862519874")
                for key, value in SherlockWrapperClassifierTest.crossmatches[0].items():
                    if key != 'rank':
                        self.assertEqual(alerts[0]['annotations']['sherlock'][0][key], value)
                # classify should have been called once
                mock_classifier.return_value.classify.assert_called_once()
                # execute should have been called twice
                self.assertEqual(mock_pymysql.return_value.cursor.return_value.__enter__.return_value.execute.call_count, 2)
                # fetchall should have been called once
                mock_pymysql.return_value.cursor.return_value.__enter__.return_value.fetchall.assert_called_once()


class SherlockWrapperProducerTest(unittest.TestCase):
    conf = {
        'broker': '',
        'group': '',
        'input_topic': '',
        'output_topic': '',
        'batch_size': 5,
        'timeout': 1,
        'max_errors': -1,
        'cache_db': ''
        }

    def test_produce_alert_batch(self):
        """test producing a batch of alerts"""
        with unittest.mock.patch('wrapper.Producer') as mock_kafka_producer:
            alerts = [{}, {}, {}]
            self.assertEqual(len(alerts), 3)
            # should report producing 3 alerts
            self.assertEqual(wrapper.produce(self.conf, log, alerts), 3)
            # alerts should now be empty
            self.assertEqual(alerts, [])
            self.assertEqual(len(alerts), 0)
            # produce should have been called 3 times
            self.assertEqual(mock_kafka_producer.return_value.produce.call_count, 3)


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
