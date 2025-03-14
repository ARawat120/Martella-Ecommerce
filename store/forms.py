from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("This field is required.")
        return name

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("This field is required.")
        return image

    class Meta:
        model = Product
        fields = ['name', 'image']
