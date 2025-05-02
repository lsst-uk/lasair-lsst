import context
import slack_webhook
import unittest
import unittest.mock as mock


class SlackWebhookTest(unittest.TestCase):
    """Tests for Slack Webhook"""
    
    @mock.patch('slack_webhook.requests.post')
    def test_send_ok(self, mock_post):
        """Test calling send normally"""
        mock_post.return_value.status_code = 200
        sw = slack_webhook.SlackWebhook("myurl", "mychannel")
        sw.send("testmessage")
        mock_post.assert_called_once()

    @mock.patch('slack_webhook.requests.post')
    def test_send_error(self, mock_post):
        """Test error handling on send"""
        mock_post.return_value.status_code = 500
        sw = slack_webhook.SlackWebhook("myurl")
        with self.assertRaises(slack_webhook.SlackError):
            sw.send("testmessage")
        mock_post.assert_called_once()

    @mock.patch('slack_webhook.requests.post')
    @mock.patch('slack_webhook.warnings.warn')
    def test_deprecated_send(self, mock_warn, mock_post):
        """Test deprecated version of send works and generates a warning"""
        mock_post.return_value.status_code = 200
        slack_webhook.send("myurl", "testmessage")
        mock_warn.assert_called_once()
        mock_post.assert_called_once()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
