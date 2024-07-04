from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Cart, Profile
from .forms import ProductForm, CartForm, UserRegisterForm, ProfileForm, PaymentForm
from django.db.models import Q
from django.http import JsonResponse
import re
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Crear perfil automáticamente al crear un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def home(request):
    return render(request, 'store/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Crear perfil al registrar usuario
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += form.cleaned_data['quantity']
            else:
                cart_item.quantity = form.cleaned_data['quantity']
            cart_item.save()
            return redirect('cart_detail')
    else:
        form = CartForm()
    return render(request, 'store/add_to_cart.html', {'product': product, 'form': form})


@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')


def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category=category)

    currency = request.user.profile.preferred_currency if request.user.is_authenticated else 'NIO'

    categories = Product.CATEGORY_CHOICES
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories, 'currency': currency})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    currency = request.user.profile.preferred_currency
    exchange_rate = 0.027  # Ejemplo de tasa de cambio de Córdobas a Dólares
    return render(request, 'store/cart_detail.html',
                  {'cart_items': cart_items, 'currency': currency, 'exchange_rate': exchange_rate})


@login_required
def checkout(request):
    if request.method == 'POST':
        return redirect('payment')
    return render(request, 'store/checkout.html')


@login_required
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            card_type = get_card_type(card_number)
            if not card_type:
                messages.error(request, 'Número de tarjeta inválido.')
            else:
                # Procesar el pago aquí (Simulación)
                Cart.objects.filter(user=request.user).delete()
                messages.success(request, f'Compra exitosa con {card_type}.')
                return redirect('home')
    else:
        form = PaymentForm()
    return render(request, 'store/payment.html', {'form': form})


def get_card_type(card_number):
    card_number = re.sub(r'\D', '', card_number)
    if re.match(r'^4[0-9]{12}(?:[0-9]{3})?$', card_number):
        return 'Visa'
    elif re.match(r'^5[1-5][0-9]{14}$', card_number):
        return 'Mastercard'
    elif re.match(r'^3[47][0-9]{13}$', card_number):
        return 'American Express'
    elif re.match(r'^6(?:011|5[0-9]{2})[0-9]{12}$', card_number):
        return 'Discover'
    return None


@login_required
@user_passes_test(lambda u: u.is_staff)
def register_admin(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form, 'is_admin': True})


@login_required
def profile(request):
    return render(request, 'store/profile.html')


@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de perfil actualizada.')
            return redirect('profile_settings')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'store/profile_settings.html', {'form': form})
