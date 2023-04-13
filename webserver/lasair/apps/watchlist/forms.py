from django import forms
from .models import Watchlist
from crispy_forms.helper import FormHelper
from django.db.models import Q


class WatchlistForm(forms.ModelForm):

    cones_textarea = forms.CharField(widget=forms.Textarea(attrs={'rows': 7, 'placeholder': 'Paste a source list. RA and Dec in decimal degrees, a unique source ID and an optional source-specific association radius in arcsec\n\nRA, Dec, ID <,radius>\nRA, Dec, ID <,radius>\n...'}))
    cones_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['cones_textarea'].required = False
        self.fields['cones_file'].required = False
        self.fields['cones_textarea'].required = False

    class Meta:
        model = Watchlist
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': True}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput(),
            'radius': forms.NumberInput(attrs={'required': True})
        }
        fields = ['name', 'description', 'active', 'public', 'radius', 'cones_textarea', 'cones_file']

    def clean(self):
        cleaned_data = super(WatchlistForm, self).clean()
        conetext = cleaned_data.get("cones_textarea")
        conefile = cleaned_data.get("cones_file")
        if not conetext and not conefile:
            msg = "Please either paste your catalogue contents or upload a catalogue file."
            self.add_error('cones_textarea', msg)

        if conetext:
            cone_list = []
            for line in conetext.split('\n'):
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                line = line.replace('|', ',')
                tok = line.split(',')
                if len(tok) < 3:
                    msg = 'Lines must be in the format RA,DEC,ID<,radius>'
                    self.add_error('cones_textarea', msg)
                    continue
                try:
                    ra = float(tok[0])
                    dec = float(tok[1])
                    objectId = tok[2].strip()
                    if len(tok) >= 4 and len(tok[3].strip()) > 0 and tok[3].strip().lower() != "none":
                        radius = float(tok[3])
                    else:
                        radius = None
                    cone_list.append([objectId, ra, dec, radius])
                except Exception as e:
                    msg = 'Lines must be in the format RA,DEC,ID <,radius>'
                    self.add_error('cones_textarea', msg)

        name = self.cleaned_data.get('name')
        if self.request:
            action = self.request.POST.get('action')

        if action == "save":
            if Watchlist.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists():
                msg = 'You already have a watchlist by that name, please choose another.'
                self.add_error('name', msg)

        return cleaned_data

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(WatchlistForm, self).save(commit=commit)


class UpdateWatchlistForm(forms.ModelForm):

    class Meta:
        model = Watchlist
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': True}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput(),
            'radius': forms.NumberInput(attrs={'required': True})
        }
        fields = ['name', 'description', 'active', 'public', 'radius']

    def clean(self):
        cleaned_data = super(UpdateWatchlistForm, self).clean()
        name = self.cleaned_data.get('name')
        if self.request:
            action = self.request.POST.get('action')

        if action == "save":
            if Watchlist.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists() and name != self.instance.name:
                msg = 'You already have a watchlist by that name, please choose another.'
                self.add_error('name', msg)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.instance = kwargs.get('instance', {})

        for i in self.fields:

            if i in ["public", "active"]:
                if self.instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False

            else:
                self.fields[i].widget.attrs['value'] = self.instance.__dict__[i]


class DuplicateWatchlistForm(forms.ModelForm):

    class Meta:
        model = Watchlist
        widgets = {
            'active': forms.CheckboxInput(),
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': True}),
            'public': forms.CheckboxInput(),
        }
        fields = ['name', 'description', 'active', 'public']

    def clean_active(self):
        return 1 if self.cleaned_data['active'] else 0

    def clean_public(self):
        return 1 if self.cleaned_data['public'] else 0

    def clean(self):
        cleaned_data = super(DuplicateWatchlistForm, self).clean()
        name = self.cleaned_data.get('name')
        if self.request:
            action = self.request.POST.get('action')

        if action == "copy":
            if Watchlist.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists():
                msg = 'You already have a watchlist by that name, please choose another.'
                self.add_error('name', msg)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        instance = kwargs.get('instance', {})

        for i in self.fields:
            if i in ["public", "active"]:
                self.initial[i] = False
            else:
                self.fields[i].widget.attrs['value'] = instance.__dict__[i]
