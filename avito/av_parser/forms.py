from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'name',
            'year',
            'city',
            'nominal',
            'bank',
            'nb',
            'metall',
            'price',
        )
        widgets = {
            'title': forms.TextInput,
        }