from django import forms
from django.contrib.auth.models import Group

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'description', 'discount',


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'delivery_address', 'promocode', 'user', 'products',


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = 'name',

# from django.core import validators

# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=1, max_value=1000000)
#     description = forms.CharField(
#         label="Product Description",
#         widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}),
#         validators=[validators.RegexValidator(
#             regex=r'great',
#             message='Field must contain word "great"'
#         )],
#     )
#     discount = forms.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         min_value=1,
#         max_value=1000000,
#     )
