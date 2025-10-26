from django import forms
from mysite.models import Projects

class SearchForm(forms.Form):
  query = forms.CharField()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['user', 'title', 'status', 'template']
