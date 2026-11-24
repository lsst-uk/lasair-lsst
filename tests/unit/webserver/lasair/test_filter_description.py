"""Unit tests for rejecting the example text as a filter name or description."""
import importlib
import sys
import types
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

from django.core.exceptions import ValidationError

sys.path.insert(0, '../../../../webserver')

EXAMPLE = 'A detailed description of your filter.'
EXAMPLE_NAME = 'Make it memorable'
FORM_NAMES = ('filterQueryForm', 'UpdateFilterQueryForm', 'DuplicateFilterQueryForm')


class FakeModelForm:
    """Stands in for django.forms.ModelForm so the form module imports without a database."""

    def clean(self):
        return self.cleaned_data


class FakeWidget:
    """Records the attrs a form widget was built with."""

    def __init__(self, attrs=None, **kwargs):
        self.attrs = dict(attrs or {})


def module(**attributes):
    result = types.ModuleType('stub')
    result.__dict__.update(attributes)
    return result


def load_forms():
    """Load the filter_query forms module with framework and infrastructure edges stubbed."""
    forms = module(
        ModelForm=FakeModelForm, ValidationError=ValidationError,
        TextInput=FakeWidget, Textarea=FakeWidget, CheckboxInput=mock.Mock(),
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


def clean_name_of(formsModule, text):
    """Run clean_name on a bare form that holds the given name."""
    class Probe(formsModule.DescriptionPlaceholderMixin):
        pass

    probe = Probe()
    probe.cleaned_data = {'name': text}
    return probe.clean_name()


def form_without_a_name(formsModule, formName, action):
    """Build a form that failed name validation, so cleaned_data has no name."""
    form = getattr(formsModule, formName).__new__(getattr(formsModule, formName))
    form.request = types.SimpleNamespace(
        POST={'action': action}, user=types.SimpleNamespace(username='demo'))
    form.cleaned_data = {'selected': 'objects.diaObjectId', 'conditions': ''}
    form.instance = types.SimpleNamespace(name='')
    return form


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

    def test_every_form_shows_the_same_description_placeholder_the_check_rejects(self):
        # ASSERT
        self.assertEqual(self.forms.EXAMPLE_DESCRIPTION, EXAMPLE)
        for name in FORM_NAMES:
            with self.subTest(form=name):
                widget = getattr(self.forms, name).Meta.widgets['description']
                self.assertEqual(widget.attrs['placeholder'], EXAMPLE)

    def test_no_form_prefills_the_name_box_with_the_example_text(self):
        for name in FORM_NAMES:
            with self.subTest(form=name):
                widget = getattr(self.forms, name).Meta.widgets['name']
                self.assertNotIn('value', widget.attrs)
                self.assertEqual(widget.attrs['placeholder'], EXAMPLE_NAME)

    def test_rejects_the_example_name(self):
        # ACT / ASSERT
        with self.assertRaises(ValidationError) as caught:
            clean_name_of(self.forms, f'  {EXAMPLE_NAME} ')
        self.assertIn('choose a name', caught.exception.messages[0])

    def test_accepts_a_real_name(self):
        # ACT / ASSERT
        self.assertEqual(clean_name_of(self.forms, 'Fast risers'), 'Fast risers')

    def test_accepts_a_name_that_only_contains_the_example_text(self):
        # ARRANGE
        text = f'{EXAMPLE_NAME} for me'

        # ACT / ASSERT
        self.assertEqual(clean_name_of(self.forms, text), text)

    def test_saving_with_a_rejected_name_does_not_crash_the_form(self):
        for formName, action in [('UpdateFilterQueryForm', 'save'),
                                 ('DuplicateFilterQueryForm', 'copy'),
                                 ('filterQueryForm', 'save')]:
            with self.subTest(form=formName):
                form = form_without_a_name(self.forms, formName, action)

                with mock.patch.object(self.forms, 'check_query', return_value=None), \
                        mock.patch.object(self.forms, 'check_query_zero_limit', return_value=None), \
                        mock.patch.object(self.forms, 'build_query'), \
                        mock.patch.object(self.forms, 'tag_topic'):
                    # ACT
                    cleaned = form.clean()

                # ASSERT
                self.assertNotIn('name', cleaned)


def load_real_forms():
    """Load the filter_query forms module on real Django, stubbing only the database and other apps."""
    from django.conf import settings as djangoSettings
    if not djangoSettings.configured:
        djangoSettings.configure(
            DEBUG=False, SECRET_KEY='test', DATABASES={}, USE_TZ=True,
            INSTALLED_APPS=[
                'django.contrib.auth', 'django.contrib.contenttypes',
                'lasair.apps.filter_query'])
        import django
        django.setup()
    emptyModel = mock.MagicMock()
    modules = {
        'crispy_forms': module(),
        'crispy_forms.helper': module(FormHelper=mock.Mock()),
        'src.db_connect': module(readonly=mock.Mock()),
        'src.annotate_util': module(
            tag_topic=mock.Mock(), count_classification=mock.Mock(), MARK_FAVOURITE='f'),
        'lasair.apps.filter_query.utils': module(check_query_zero_limit=mock.Mock(return_value=None)),
        'lasair.apps.annotator.models': module(Annotators=emptyModel),
        'lasair.apps.watchmap.models': module(Watchmap=emptyModel),
        'lasair.apps.watchlist.models': module(Watchlist=emptyModel),
        'lasair.apps.favourites.utils': module(offered_annotators=mock.Mock(return_value=[])),
        'lasair.query_builder': module(
            check_query=mock.Mock(return_value=None), build_query=mock.Mock(),
            FAVOURITE_ONLY='fav', HIDDEN_INCLUDE='hid'),
    }
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop('lasair.apps.filter_query.forms', None)
        return importlib.import_module('lasair.apps.filter_query.forms')


class RealFilterFormTest(unittest.TestCase):
    """The example name submitted through a real Django ModelForm, which needs no database."""

    @classmethod
    def setUpClass(cls):
        cls.forms = load_real_forms()

    def test_rejects_the_example_name_without_crashing_and_without_prefilling_the_box(self):
        # ARRANGE
        request = types.SimpleNamespace(
            POST={'action': 'save'},
            user=types.SimpleNamespace(username='demo', is_authenticated=False))
        form = self.forms.filterQueryForm(
            data={'name': EXAMPLE_NAME, 'description': 'Fast risers.', 'run': 0, 'output': 0,
                  'selected': 'objects.diaObjectId', 'conditions': ''},
            request=request)

        # ACT
        isValid = form.is_valid()
        cleaned = form.clean()

        # ASSERT
        self.assertFalse(isValid)
        self.assertIn('choose a name', form.errors['name'][0])
        self.assertNotIn('name', cleaned)
        self.assertNotIn('value', form.fields['name'].widget.attrs)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
