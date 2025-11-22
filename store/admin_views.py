# store/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Category
from orders.models import Order, OrderItem
from django.contrib.auth.models import User
from cart.models import CartItem


@staff_member_required
def admin_dashboard(request):
    # Statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    # Revenue statistics
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    today = timezone.now().date()
    today_revenue = Order.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]

    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=10, available=True).order_by('stock')[:5]

    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Count('orderitem')
    ).order_by('-total_sold')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required
def admin_products(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
    }
    return render(request, 'admin_panel/products.html', context)


@staff_member_required
def admin_product_add(request):
    if request.method == 'POST':
        from django.utils.text import slugify

        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        featured = request.POST.get('featured') == 'on'
        available = request.POST.get('available') == 'on'

        category = get_object_or_404(Category, id=category_id)

        product = Product.objects.create(
            name=name,
            slug=slugify(name),
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image,
            featured=featured,
            available=available
        )

        messages.success(request, f'Product "{name}" added successfully!')
        return redirect('admin_panel:products')

    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'admin_panel/product_form.html', context)


@staff_member_required
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        from django.utils.text import slugify

        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.featured = request.POST.get('featured') == 'on'
        product.available = request.POST.get('available') == 'on'
        product.slug = slugify(product.name)
        product.save()

        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('admin_panel:products')

    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'edit_mode': True
    }
    return render(request, 'admin_panel/product_form.html', context)


@staff_member_required
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f'Product "{name}" deleted successfully!')
    return redirect('admin_panel:products')


@staff_member_required
def admin_orders(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    orders = Order.objects.select_related('user').prefetch_related('items').all()

    if status_filter:
        orders = orders.filter(status=status_filter)

    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(user__username__icontains=query) |
            Q(email__icontains=query)
        )

    orders = orders.order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'admin_panel/orders.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}')
        return redirect('admin_panel:order_detail', order_id=order_id)

    context = {'order': order}
    return render(request, 'admin_panel/order_detail.html', context)


@staff_member_required
def admin_users(request):
    query = request.GET.get('q', '')

    users = User.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    )

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    users = users.order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'admin_panel/users.html', context)


@staff_member_required
def admin_categories(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')

    context = {'categories': categories}
    return render(request, 'admin_panel/categories.html', context)


@staff_member_required
def admin_category_add(request):
    if request.method == 'POST':
        from django.utils.text import slugify

        name = request.POST.get('name')
        description = request.POST.get('description')

        Category.objects.create(
            name=name,
            slug=slugify(name),
            description=description
        )

        messages.success(request, f'Category "{name}" added successfully!')
        return redirect('admin_panel:categories')

    return render(request, 'admin_panel/category_form.html')


@staff_member_required
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        from django.utils.text import slugify

        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.slug = slugify(category.name)
        category.save()

        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('admin_panel:categories')

    context = {
        'category': category,
        'edit_mode': True
    }
    return render(request, 'admin_panel/category_form.html', context)


@staff_member_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted successfully!')
    return redirect('admin_panel:categories')


# Create a new urls file for admin panel
# admin_panel/urls.py
from django.urls import path
from store import admin_views

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('products/', admin_views.admin_products, name='products'),
    path('products/add/', admin_views.admin_product_add, name='product_add'),
    path('products/edit/<int:product_id>/', admin_views.admin_product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', admin_views.admin_product_delete, name='product_delete'),
    path('orders/', admin_views.admin_orders, name='orders'),
    path('orders/<str:order_id>/', admin_views.admin_order_detail, name='order_detail'),
    path('users/', admin_views.admin_users, name='users'),
    path('categories/', admin_views.admin_categories, name='categories'),
    path('categories/add/', admin_views.admin_category_add, name='category_add'),
    path('categories/edit/<int:category_id>/', admin_views.admin_category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', admin_views.admin_category_delete, name='category_delete'),
]