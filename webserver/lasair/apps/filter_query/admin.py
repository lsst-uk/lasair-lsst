from django.contrib import admin
from .models import filter_query
#admin.site.register(filter_query)

from django import forms
class filter_queryModelForm( forms.ModelForm ):
    description = forms.CharField( widget=forms.Textarea )
    selected    = forms.CharField( widget=forms.Textarea )
    conditions  = forms.CharField( widget=forms.Textarea )
    real_sql    = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = filter_query
        fields = '__all__'

class filter_query_Admin( admin.ModelAdmin ):
    form = filter_queryModelForm

admin.site.register(filter_query, filter_query_Admin)

