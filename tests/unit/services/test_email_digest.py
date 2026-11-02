import context
import unittest
import unittest.mock as mock
import email_digest


class SuppressHiddenTest(unittest.TestCase):
    """Tests for the digest's second pass over a filter's Kafka messages."""

    @mock.patch('email_digest.annotate_util.marks_for_objects')
    def test_removes_the_users_hidden_objects(self, mock_marks):
        """An object hidden by the recipient does not reach their inbox"""
        # ARRANGE
        mock_marks.return_value = {2: 'hidden', 3: 'favourite'}
        alerts = [{'diaObjectId': 1}, {'diaObjectId': 2}, {'diaObjectId': 3}]

        # ACT
        kept, omitted = email_digest.suppress_hidden(alerts, 'tags_dave')

        # ASSERT
        self.assertEqual(kept, [{'diaObjectId': 1}, {'diaObjectId': 3}])
        self.assertEqual(omitted, 1)

    @mock.patch('email_digest.annotate_util.marks_for_objects')
    def test_matches_the_id_key_case_insensitively(self, mock_marks):
        """format_line already matches diaObjectId case-insensitively"""
        # ARRANGE
        mock_marks.return_value = {2: 'hidden'}
        alerts = [{'diaobjectid': 2}]

        # ACT
        kept, omitted = email_digest.suppress_hidden(alerts, 'tags_dave')

        # ASSERT
        self.assertEqual(kept, [])
        self.assertEqual(omitted, 1)

    @mock.patch('email_digest.annotate_util.marks_for_objects')
    def test_messages_with_no_object_id_pass_through(self, mock_marks):
        """There is nothing to match on, and dropping on a guess would be worse"""
        # ARRANGE
        mock_marks.return_value = {}
        alerts = [{'name': 'something'}]

        # ACT
        kept, omitted = email_digest.suppress_hidden(alerts, 'tags_dave')

        # ASSERT
        self.assertEqual(kept, alerts)
        self.assertEqual(omitted, 0)

    @mock.patch('email_digest.annotate_util.marks_for_objects')
    def test_ids_are_looked_up_in_chunks(self, mock_marks):
        """A digest topic is unbounded, so the bounded helper is chunked"""
        # ARRANGE
        mock_marks.return_value = {}
        alerts = [{'diaObjectId': i} for i in range(2500)]

        # ACT
        email_digest.suppress_hidden(alerts, 'tags_dave')

        # ASSERT
        chunkSizes = [len(call[0][1]) for call in mock_marks.call_args_list]
        self.assertEqual(chunkSizes, [1000, 1000, 500])

    @mock.patch('email_digest.annotate_util.marks_for_objects')
    def test_no_lookup_for_an_empty_digest(self, mock_marks):
        # ACT
        kept, omitted = email_digest.suppress_hidden([], 'tags_dave')

        # ASSERT
        self.assertEqual(kept, [])
        self.assertEqual(omitted, 0)
        mock_marks.assert_not_called()


@mock.patch.object(email_digest.settings, 'LASAIR_URL', 'lasair.example', create=True)
class FormatMessageTest(unittest.TestCase):
    """Tests for the line telling the user what was left out."""

    def test_the_omitted_count_is_stated_in_both_bodies(self):
        # ACT
        text, html = email_digest.format_message('my filter', [{'diaObjectId': 1}], omitted=3)

        # ASSERT
        self.assertIn('3 hidden objects omitted', text)
        self.assertIn('3 hidden objects omitted', html)

    def test_nothing_is_said_when_nothing_was_omitted(self):
        # ACT
        text, html = email_digest.format_message('my filter', [{'diaObjectId': 1}], omitted=0)

        # ASSERT
        self.assertNotIn('omitted', text)
        self.assertNotIn('omitted', html)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
