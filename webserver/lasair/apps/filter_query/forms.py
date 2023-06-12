from django import forms
from .models import filter_query
from crispy_forms.helper import FormHelper
from src import db_connect
from lasair.apps.annotator.models import Annotators
from lasair.apps.watchmap.models import Watchmap
from lasair.apps.watchlist.models import Watchlist
from django.db.models import Q
from lasair.query_builder import check_query, build_query
from .utils import check_query_zero_limit
import re


class filterQueryForm(forms.ModelForm):

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchlists = forms.ChoiceField(widget=forms.Select)
    watchmaps = forms.MultipleChoiceField(widget=forms.SelectMultiple)
    annotators = forms.MultipleChoiceField(widget=forms.SelectMultiple)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        if 'instance' in kwargs:
            self.instance = kwargs.get('instance', None)

            if self.instance:
                for i in self.fields:
                    if i in ["public"]:
                        if self.instance.__dict__[i]:
                            self.initial[i] = True
                        else:
                            self.initial[i] = False
                    elif i not in ["watchlists", "watchmaps", "annotators"]:
                        self.fields[i].widget.attrs['value'] = self.instance.__dict__[i]

                # PARSE WATCHLISTS, WATCHMAPS, ANNOTATORS
                if "watchlist:" in self.instance.tables:
                    try:
                        self.initial["watchlists"] = int(self.instance.tables.split("watchlist:")[1].split(",")[0])
                    except:
                        pass

                if "area:" in self.instance.tables:

                    try:
                        currentWatchmaps = self.instance.tables.split("area:")[1].split(",")[0].split("&")
                        currentWatchmaps[:] = [int(m) for m in currentWatchmaps]
                        self.initial["watchmaps"] = currentWatchmaps
                    except:
                        pass
                if "annotator:" in self.instance.tables:
                    try:
                        currentAnnotators = self.instance.tables.split("annotator:")[1].split(",")[0].split("&")
                        self.initial["annotators"] = currentAnnotators
                    except:
                        pass

        if self.request.user.is_authenticated:
            email = self.request.user.email
            watchlists = Watchlist.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
            watchmaps = Watchmap.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
            annotators = Annotators.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
        else:
            email = ''
            watchlists = Watchlist.objects.filter(public__gte=1)
            watchmaps = Watchmap.objects.filter(public__gte=1)
            annotators = Annotators.objects.filter(public__gte=1)

        # ADD WATCHLIST SELECTION TO THE FORM
        watchlistTypes, watchlistTypes2 = [], []
        if self.request.user.is_authenticated:
            watchlistTypes[:] = [(w.wl_id, w.name) for w in watchlists if w.user.id == self.request.user.id]
        watchlistTypes2[:] = [(w.wl_id, w.name + f" ({w.user})") for w in watchlists if w.user.id != self.request.user.id]
        watchlistTypes = [(None, "No Watchlist Selected    ")] + [("My Watchlists", watchlistTypes)] + [("Public Gallery", watchlistTypes2)]
        self.fields['watchlists'].required = False
        self.fields['watchlists'].choices = watchlistTypes
        self.fields['watchlists'].widget.choices = watchlistTypes

        # ADD WATCHMAP SELECTION TO THE FORM
        watchmapTypes, watchmapTypes2 = [], []
        if self.request.user.is_authenticated:
            watchmapTypes[:] = [(w.ar_id, w.name) for w in watchmaps if w.user.id == self.request.user.id]
        watchmapTypes2[:] = [(w.ar_id, w.name + f" ({w.user})") for w in watchmaps if w.user.id != self.request.user.id]
        watchmapTypes = [("My Watchmap", watchmapTypes)] + [("Public Gallery", watchmapTypes2)]
        self.fields['watchmaps'].required = False
        self.fields['watchmaps'].choices = watchmapTypes
        self.fields['watchmaps'].widget.choices = watchmapTypes

        # ADD ANNOTATOR SELECTION TO THE FORM
        annotatorTypes, annotatorTypes2 = [], []
        if self.request.user.is_authenticated:
            annotatorTypes[:] = [(w.topic, w.topic) for w in annotators if w.user.id == self.request.user.id]
        annotatorTypes2[:] = [(w.topic, w.topic + f" ({w.user})") for w in annotators if w.user.id != self.request.user.id]
        annotatorTypes = [("My Annotators", annotatorTypes)] + [("Public Gallery", annotatorTypes2)]
        self.fields['annotators'].required = False
        self.fields['annotators'].choices = annotatorTypes
        self.fields['annotators'].widget.choices = annotatorTypes

        self.fields['conditions'].required = False
        self.fields['conditions'].widget.required = False

    class Meta:

        notificationTypes = (
            (0, 'muted'),
            (1, 'email stream (daily)'),
            (2, 'kafka stream')
        )
        model = filter_query
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': 'true', 'value': "Make it memorable"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': 'true'}),
            'public': forms.CheckboxInput(),
            'selected': forms.Textarea(),
            'conditions': forms.Textarea(),
            'real_sql': forms.Textarea(),
            'active': forms.Select(choices=notificationTypes)
        }
        fields = ['name', 'description', 'active', 'public', 'selected', 'conditions', 'real_sql', 'watchlists', 'watchmaps']

    def clean(self):

        cleaned_data = super(filterQueryForm, self).clean()

        if self.request:
            action = self.request.POST.get('action')
        name = self.cleaned_data.get('name')

        if action == "save":
            if filter_query.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists() and self.instance.name != name:
                msg = 'You already have a filter by that name, please choose another.'
                self.add_error('name', msg)

        if action in ["run", "save"]:
            selected = self.cleaned_data.get('selected')
            conditions = self.cleaned_data.get('conditions')
            # FIND THE TABLES THAT NEED TO BE QUIERIED FROM THE SELECT STATEMENT
            matchObjectList = re.findall(r'([a-zA-Z0-9_\-]*)\.([a-zA-Z0-9_\-]*)', selected)
            tables = [m[0] for m in matchObjectList]
            tables = (",").join(set(tables))

            e = check_query(selected, tables, conditions)
            if e:
                try:
                    msg = e.split("syntax to use near '")[1].split("' at line")[0]
                except:
                    msg = e
                try:
                    msg = e.split("returned the error")[1].split(": ")[1].replace("</i>", "")
                except:
                    msg = e
                self.add_error('selected', msg)

            sqlquery_real = build_query(selected, tables, conditions)
            e = check_query_zero_limit(sqlquery_real)
            if e:
                try:
                    msg = e.split("syntax to use near '")[1].split("' at line")[0]
                except:
                    msg = e
                try:
                    msg = e.split("returned the error")[1].split(": ")[1].replace("</i>", "")
                except:
                    msg = e
                self.add_error('selected', msg)

        return cleaned_data

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(filterQueryForm, self).save(commit=commit)


class UpdateFilterQueryForm(forms.ModelForm):

    class Meta:
        notificationTypes = (
            (0, 'muted'),
            (1, 'email stream (daily)'),
            (2, 'kafka stream')
        )
        model = filter_query
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': 'true', 'value': "Make it memorable"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': 'true'}),
            'public': forms.CheckboxInput(),
            'active': forms.Select(choices=notificationTypes)
        }
        fields = ['name', 'description', 'active', 'public']

    def clean(self):
        cleaned_data = super(UpdateFilterQueryForm, self).clean()
        if self.request:
            action = self.request.POST.get('action')
        name = self.cleaned_data.get('name')

        if action == "save":
            if filter_query.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists() and self.instance.name != name:
                msg = 'You already have a filter by that name, please choose another.'
                self.add_error('name', msg)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.instance = kwargs.get('instance', {})

        for i in self.fields:
            if i in ["public"]:
                if self.instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False
            else:
                self.fields[i].widget.attrs['value'] = self.instance.__dict__[i]


class DuplicateFilterQueryForm(forms.ModelForm):

    class Meta:
        notificationTypes = (
            (0, 'muted'),
            (1, 'email stream (daily)'),
            (2, 'kafka stream')
        )
        model = filter_query
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': 'true', 'value': "Make it memorable"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': 'true'}),
            'public': forms.CheckboxInput(),
            'active': forms.Select(choices=notificationTypes)
        }
        fields = ['name', 'description', 'active', 'public']

    def clean(self):
        cleaned_data = super(DuplicateFilterQueryForm, self).clean()
        if self.request:
            action = self.request.POST.get('action')
        name = self.cleaned_data.get('name')

        if action == "copy":
            if filter_query.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists():
                msg = 'You already have a filter by that name, please choose another.'
                self.add_error('name', msg)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.instance = kwargs.get('instance', {})

        for i in self.fields:
            if i in ["public"]:
                if self.instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False
            else:
                self.fields[i].widget.attrs['value'] = self.instance.__dict__[i]
