from django import forms
from .models import Projects, Photos

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ["title", "template"]


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description']
        widgets = {
            'url': forms.HiddenInput,
        }

        def clean_url(self):
            url = self.cleaned_data['url']
            valid_extensions = ['jpg', 'jpeg', 'png']
            extension = url.rsplit('.', 1)[1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError('The given URL does not ' \
                    'match valid image extensions.')
            return url