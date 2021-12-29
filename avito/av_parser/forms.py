from django import forms
from .models import Product
from .models import Comments

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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = (
            'dated',
            'name',
            'url_lot',
            'url_saler',
            'current_price',
            'status',
            'stack',
            'post1_price',
            'name_saler',
            'comment_id',
            'buy',
            # 'colored_name',
        )
        widgets = {
            'title': forms.TextInput,
        }