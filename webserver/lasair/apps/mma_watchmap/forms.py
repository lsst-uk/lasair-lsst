from django import forms
from .models import MmaWatchmap
from crispy_forms.helper import FormHelper
from django.db.models import Q


class MmaWatchmapForm(forms.ModelForm):

    watchmap_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['watchmap_file'].required = True

    class Meta:
        model = MmaWatchmap
        widgets = {
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['active', 'public', 'watchmap_file']

    def clean(self):
        cleaned_data = super(MmaWatchmapForm, self).clean()

        if self.request:
            action = self.request.POST.get('action')

        if action == "save":
            if MmaWatchmap.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists():
                msg = 'You already have a watchmap by that name, please choose another.'
                self.add_error('name', msg)

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(MmaWatchmapForm, self).save(commit=commit)


class UpdateMmaWatchmapForm(forms.ModelForm):

    class Meta:
        model = MmaWatchmap
        widgets = {
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['active', 'public']

    def clean(self):
        cleaned_data = super(UpdateMmaWatchmapForm, self).clean()

        if self.request:
            action = self.request.POST.get('action')

        if action == "save":
            if MmaWatchmap.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists() and self.instance.name != name:
                msg = 'You already have a watchmap by that name, please choose another.'
                self.add_error('name', msg)

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


class DuplicateMmaWatchmapForm(forms.ModelForm):

    class Meta:
        model = MmaWatchmap
        widgets = {
            'active': forms.CheckboxInput(),
            'public': forms.CheckboxInput(),
        }
        fields = ['active', 'public']

    def clean_active(self):
        return 1 if self.cleaned_data['active'] else 0

    def clean_public(self):
        return 1 if self.cleaned_data['public'] else 0

    def clean(self):
        cleaned_data = super(DuplicateMmaWatchmapForm, self).clean()
        if self.request:
            action = self.request.POST.get('action')

        if action == "copy":
            if MmaWatchmap.objects.filter(Q(user=self.request.user) & Q(name__iexact=name.strip().lower())).exists():
                msg = 'You already have a watchmap by that name, please choose another.'
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
