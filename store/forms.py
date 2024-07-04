import re

from django import forms
from .models import Product, Cart, Profile
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

class PaymentForm(forms.Form):
    card_number = forms.CharField(
        label='Número de Tarjeta',
        max_length=19,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    expiry_date = forms.CharField(
        label='Fecha de Expiración (MM/AA)',
        max_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cvv = forms.CharField(
        label='CVV',
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if not re.match(r'(0[1-9]|1[0-2])\/?([0-9]{2})', expiry_date):
            raise forms.ValidationError('Fecha de expiración inválida.')
        return expiry_date

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if not re.match(r'^[0-9]{13,19}$', card_number):
            raise forms.ValidationError('Número de tarjeta inválido.')
        return card_number

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not re.match(r'^[0-9]{3,4}$', cvv):
            raise forms.ValidationError('CVV inválido.')
        return cvv


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['preferred_currency']