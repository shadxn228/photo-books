from django import forms
from .models import Projects, Photos

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ["title", "template"]
