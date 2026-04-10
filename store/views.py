from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Product, Category, Brand, Cart, Order, OrderItem
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .forms import RegisterForm, LoginForm, ProductForm, CategoryForm, BrandForm


# ─── REGISTER ─────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'customer'
            user.save()
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
    return render(request, 'store/register.html', {'form': form})


# ─── LOGIN ────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user     = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin' or user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html', {'form': form})


# ─── LOGOUT ───────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── HOME ─────────────────────────────────────────────────────
@login_required
def home_view(request):
    if request.user.role == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard')
    products   = Product.objects.filter(stock_quantity__gt=0)
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    # cart count for navbar
    cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'store/home.html', {
        'products'   : products,
        'categories' : categories,
        'cart_count' : cart_count,
    })


# ─── PRODUCT DETAIL ───────────────────────────────────────────
@login_required
def product_detail_view(request, pk):
    product    = get_object_or_404(Product, pk=pk)
    cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'store/product_detail.html', {
        'product'   : product,
        'cart_count': cart_count,
    })


# ─── ADD TO CART ──────────────────────────────────────────────
@login_required
def add_to_cart_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{product.product_name}" added to cart!')
    return redirect('cart')


# ─── CART ─────────────────────────────────────────────────────
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total      = sum(item.get_total() for item in cart_items)
    cart_count = cart_items.count()
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total'     : total,
        'cart_count': cart_count,
    })


# ─── UPDATE CART QUANTITY ─────────────────────────────────────
@login_required
def update_cart_view(request, pk):
    cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
    action    = request.POST.get('action')
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


# ─── REMOVE FROM CART ─────────────────────────────────────────
@login_required
def remove_from_cart_view(request, pk):
    cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ─── CHECKOUT ─────────────────────────────────────────────────
@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')

    total = sum(item.get_total() for item in cart_items)

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        if not shipping_address:
            messages.error(request, 'Please enter a shipping address.')
            return redirect('checkout')

        # Create Order
        order = Order.objects.create(
            user             = request.user,
            total_amount     = total,
            shipping_address = shipping_address,
            status           = 'pending',
        )

        # Create Order Items & reduce stock
        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                product  = item.product,
                quantity = item.quantity,
                price    = item.product.price,
            )
            # reduce stock
            item.product.stock_quantity -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('my_orders')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total'     : total,
    })


# ─── MY ORDERS ────────────────────────────────────────────────
@login_required
def my_orders_view(request):
    orders     = Order.objects.filter(user=request.user).order_by('-created_at')
    cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'store/my_orders.html', {
        'orders'    : orders,
        'cart_count': cart_count,
    })


# ─── ADMIN DASHBOARD ──────────────────────────────────────────
@login_required
def admin_dashboard_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    products      = Product.objects.all()
    total_orders  = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_users   = Order.objects.values('user').distinct().count()
    return render(request, 'store/admin_dashboard.html', {
        'products'      : products,
        'total_orders'  : total_orders,
        'pending_orders': pending_orders,
        'total_users'   : total_users,
    })

# ─── ADMIN: MANAGE PRODUCTS ───────────────────────────────────
@login_required
def admin_products_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'store/admin_products.html', {'products': products})


@login_required
def admin_add_product_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.added_by = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {
        'form': form, 'title': 'Add Product'
    })


@login_required
def admin_edit_product_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    form    = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {
        'form': form, 'title': 'Edit Product'
    })


@login_required
def admin_delete_product_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('admin_products')


# ─── ADMIN: MANAGE ORDERS ─────────────────────────────────────
@login_required
def admin_orders_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/admin_orders.html', {'orders': orders})


@login_required
def admin_update_order_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        messages.success(request, f'Order #{order.id} updated to {status}.')
        return redirect('admin_orders')
    return render(request, 'store/admin_order_detail.html', {'order': order})


# ─── ADMIN: MANAGE USERS ──────────────────────────────────────
@login_required
def admin_users_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    from .models import User
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'store/admin_users.html', {'users': users})


@login_required
def admin_toggle_user_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    from .models import User
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" {status}.')
    return redirect('admin_users')

# ─── ADMIN: MANAGE CATEGORIES ─────────────────────────────────
@login_required
def admin_categories_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    categories = Category.objects.all()
    form       = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('admin_categories')
    return render(request, 'store/admin_categories.html', {
        'categories': categories,
        'form'      : form,
    })


@login_required
def admin_edit_category_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    category = get_object_or_404(Category, pk=pk)
    form     = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('admin_categories')
    return render(request, 'store/admin_category_brand_form.html', {
        'form' : form,
        'title': 'Edit Category',
        'back' : 'admin_categories',
    })


@login_required
def admin_delete_category_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('admin_categories')


# ─── ADMIN: MANAGE BRANDS ─────────────────────────────────────
@login_required
def admin_brands_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    brands = Brand.objects.all()
    form   = BrandForm()
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added successfully!')
            return redirect('admin_brands')
    return render(request, 'store/admin_brands.html', {
        'brands': brands,
        'form'  : form,
    })


@login_required
def admin_edit_brand_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    brand = get_object_or_404(Brand, pk=pk)
    form  = BrandForm(instance=brand)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated!')
            return redirect('admin_brands')
    return render(request, 'store/admin_category_brand_form.html', {
        'form' : form,
        'title': 'Edit Brand',
        'back' : 'admin_brands',
    })


@login_required
def admin_delete_brand_view(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('home')
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    messages.success(request, 'Brand deleted.')
    return redirect('admin_brands')