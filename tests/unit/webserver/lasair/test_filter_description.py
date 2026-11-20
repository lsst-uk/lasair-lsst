"""Unit tests for rejecting the example text as a filter description."""
import importlib
import sys
import types
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

from django.core.exceptions import ValidationError

sys.path.insert(0, '../../../../webserver')

EXAMPLE = 'A detailed description of your filter.'


class FakeModelForm:
    """Stands in for django.forms.ModelForm so the form module imports without a database."""


def module(**attributes):
    result = types.ModuleType('stub')
    result.__dict__.update(attributes)
    return result


def load_forms():
    """Load the filter_query forms module with framework and infrastructure edges stubbed."""
    forms = module(
        ModelForm=FakeModelForm, ValidationError=ValidationError,
        TextInput=mock.Mock(), Textarea=mock.Mock(), CheckboxInput=mock.Mock(),
        Select=mock.Mock(), SelectMultiple=mock.Mock(), ChoiceField=mock.Mock(),
        MultipleChoiceField=mock.Mock(), BooleanField=mock.Mock())
    messages = module()
    modules = {
        'django': module(forms=forms),
        'django.forms': forms,
        'django.contrib': module(messages=messages),
        'django.contrib.messages': messages,
        'django.db': module(),
        'django.db.models': module(Q=mock.Mock()),
        'crispy_forms': module(),
        'crispy_forms.helper': module(FormHelper=mock.Mock()),
        'src.db_connect': module(readonly=mock.Mock()),
        'src.annotate_util': module(
            tag_topic=mock.Mock(), count_classification=mock.Mock(), MARK_FAVOURITE='f'),
        'lasair.apps.filter_query.models': module(filter_query=object),
        'lasair.apps.filter_query.utils': module(check_query_zero_limit=mock.Mock()),
        'lasair.apps.annotator.models': module(Annotators=object),
        'lasair.apps.watchmap.models': module(Watchmap=object),
        'lasair.apps.watchlist.models': module(Watchlist=object),
        'lasair.apps.favourites.utils': module(offered_annotators=mock.Mock()),
        'lasair.query_builder': module(
            check_query=mock.Mock(), build_query=mock.Mock(),
            FAVOURITE_ONLY='fav', HIDDEN_INCLUDE='hid'),
    }
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop('lasair.apps.filter_query.forms', None)
        return importlib.import_module('lasair.apps.filter_query.forms')


def clean_description_of(formsModule, text):
    """Run clean_description on a bare form that holds the given description."""
    class Probe(formsModule.DescriptionPlaceholderMixin):
        pass

    probe = Probe()
    probe.cleaned_data = {'description': text}
    return probe.clean_description()


class FilterDescriptionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.forms = load_forms()

    def test_rejects_the_example_text(self):
        # ACT / ASSERT
        with self.assertRaises(ValidationError) as caught:
            clean_description_of(self.forms, EXAMPLE)
        self.assertIn('write your own description', caught.exception.messages[0])

    def test_rejects_the_example_text_with_surrounding_whitespace(self):
        # ACT / ASSERT
        with self.assertRaises(ValidationError):
            clean_description_of(self.forms, f'  {EXAMPLE}\n')

    def test_accepts_a_real_description(self):
        # ACT
        cleaned = clean_description_of(self.forms, 'Fast risers with a host galaxy.')

        # ASSERT
        self.assertEqual(cleaned, 'Fast risers with a host galaxy.')

    def test_accepts_a_description_that_only_contains_the_example_text(self):
        # ARRANGE
        text = f'{EXAMPLE} Plus my own words.'

        # ACT / ASSERT
        self.assertEqual(clean_description_of(self.forms, text), text)

    def test_every_filter_save_form_checks_the_description(self):
        # ASSERT
        for name in ('filterQueryForm', 'UpdateFilterQueryForm', 'DuplicateFilterQueryForm'):
            with self.subTest(form=name):
                self.assertTrue(issubclass(
                    getattr(self.forms, name), self.forms.DescriptionPlaceholderMixin))


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
