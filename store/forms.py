from django import forms
from .models import Product, Cart
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
