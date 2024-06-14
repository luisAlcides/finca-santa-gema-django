from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Cart
from .forms import ProductForm, CartForm, UserRegisterForm
from django.db.models import Q
from django.http import JsonResponse


def home(request):
    return render(request, 'store/home.html')


def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category:
        products = products.filter(category=category)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_list = []
        for product in products:
            products_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.get_category_display(),
                'image': product.image.url if product.image else '',
            })
        return JsonResponse(products_list, safe=False)

    categories = Product.CATEGORY_CHOICES
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
            )
            cart_item.quantity += form.cleaned_data['quantity']
            cart_item.save()
            return redirect('cart_detail')
    else:
        form = CartForm()
    return render(request, 'store/add_to_cart.html',
                  {'product': product, 'form': form})


def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'store/cart_detail.html',
                  {'cart_items': cart_items})


def checkout(request):
    if request.method == 'POST':
        Cart.objects.filter(user=request.user).delete()
        return redirect('product_list')
    return render(request, 'store/checkout.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


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
